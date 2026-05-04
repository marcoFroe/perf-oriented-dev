#include <pthread.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>

// --- Configuration ---
#define DEFAULT_ARENA_SIZE (512 * 1024 * 1024) // 512 MB per thread
#define DEFAULT_ALIGNMENT 16

// --- Thread-Local Arena ---
typedef struct {
  void *memory;
  size_t size;
  size_t offset;
  size_t alignment;
} ThreadArena;

static __thread ThreadArena thread_arena;
static __thread bool arena_initialized = false;

// --- Thread Cleanup ---
static void cleanup_thread_arena(void) {
  if (arena_initialized && thread_arena.memory) {
    munmap(thread_arena.memory, thread_arena.size);
    memset(&thread_arena, 0, sizeof(ThreadArena));
    arena_initialized = false;
  }
}

// Destructor runs when thread exits
static void __attribute__((destructor)) thread_destructor(void) {
  cleanup_thread_arena();
}

// --- Get or Create Thread-Local Arena ---
static ThreadArena *get_thread_arena(void) {
  if (!arena_initialized) {
    // Initialize arena metadata using memset
    memset(&thread_arena, 0, sizeof(ThreadArena));

    thread_arena.size = DEFAULT_ARENA_SIZE;
    thread_arena.alignment = DEFAULT_ALIGNMENT;
    thread_arena.offset = 0;

    thread_arena.memory = mmap(NULL, thread_arena.size, PROT_READ | PROT_WRITE,
                               MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (thread_arena.memory == MAP_FAILED) {
      fprintf(stderr, "Failed to allocate thread arena memory.\n");
      exit(EXIT_FAILURE);
    }

    arena_initialized = true;
  }
  return &thread_arena;
}

// --- Custom malloc ---
void *malloc(size_t size) {
  if (size == 0)
    return NULL;

  ThreadArena *arena = get_thread_arena();
  if (!arena)
    return NULL;

  // Align current offset
  uintptr_t current_addr = (uintptr_t)arena->memory + arena->offset;
  uintptr_t aligned_addr =
      (current_addr + arena->alignment - 1) & ~(arena->alignment - 1);
  size_t aligned_offset = aligned_addr - (uintptr_t)arena->memory;

  // Overflow check
  if (aligned_offset > SIZE_MAX - size) {
    return NULL;
  }

  size_t new_offset = aligned_offset + size;
  if (new_offset > arena->size) {
    fprintf(stderr, "Thread arena out of memory.\n");
    return NULL;
  }

  void *ptr = (void *)aligned_addr;
  arena->offset = new_offset;
  return ptr;
}

// --- Custom calloc ---
void *calloc(size_t num, size_t size) {
  if (num == 0 || size == 0)
    return NULL;

  if (num > SIZE_MAX / size) {
    return NULL; // Overflow
  }

  size_t total = num * size;
  void *ptr = malloc(total);
  if (ptr) {
    memset(ptr, 0, total);
  }
  return ptr;
}

// --- Free (resets arena) ---
void free(void *ptr) {
  if (ptr == NULL)
    return;

  ThreadArena *arena = get_thread_arena();
  if (arena) {
    arena->offset = 0;
  }
}