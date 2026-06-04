#include <stdio.h>
#include <stdlib.h>

typedef unsigned long dn;

// Hash table structure for memorization
#define HASH_TABLE_SIZE 10000

typedef struct {
	dn x;
	dn y;
	dn result;
	int valid;
} HashEntry;

HashEntry hash_table[HASH_TABLE_SIZE];

// Simple hash function
unsigned int hash(dn x, dn y) {
	return (x * 31 + y) % HASH_TABLE_SIZE;
}

// Initialize hash table
void init_hash_table() {
	for(int i = 0; i < HASH_TABLE_SIZE; i++) {
		hash_table[i].valid = 0;
	}
}

// Lookup in hash table
int lookup_hash_table(dn x, dn y, dn* result) {
	unsigned int index = hash(x, y);
	if(hash_table[index].valid && hash_table[index].x == x && hash_table[index].y == y) {
		*result = hash_table[index].result;
		return 1;
	}
	return 0;
}

// Insert into hash table
void insert_hash_table(dn x, dn y, dn result) {
	unsigned int index = hash(x, y);
	hash_table[index].x = x;
	hash_table[index].y = y;
	hash_table[index].result = result;
	hash_table[index].valid = 1;
}

dn delannoy(dn x, dn y) {
	dn result;

	// Check if result is already in hash table
	if(lookup_hash_table(x, y, &result)) {
		return result;
	}

	// Base case
	if(x == 0 || y == 0) {
		result = 1;
	} else {
		// Recursive case with memorization
		dn a = delannoy(x - 1, y);
		dn b = delannoy(x - 1, y - 1);
		dn c = delannoy(x, y - 1);
		result = a + b + c;
	}

	// Store result in hash table
	insert_hash_table(x, y, result);

	return result;
}

dn DELANNOY_RESULTS[] = { 1,
	                      3,
	                      13,
	                      63,
	                      321,
	                      1683,
	                      8989,
	                      48639,
	                      265729,
	                      1462563,
	                      8097453,
	                      45046719,
	                      251595969,
	                      1409933619,
	                      7923848253,
	                      44642381823,
	                      252055236609,
	                      1425834724419,
	                      8079317057869,
	                      45849429914943,
	                      260543813797441,
	                      1482376214227923,
	                      8443414161166173 };

int NUM_RESULTS = sizeof(DELANNOY_RESULTS) / sizeof(dn);

int main(int argc, char** argv) {
	if(argc < 2) {
		printf("Usage: delannoy N [+t]\n");
		exit(-1);
	}

	int n = atoi(argv[1]);
	if(n >= NUM_RESULTS) {
		printf("N too large (can only check up to %d)\n", NUM_RESULTS);
		exit(-1);
	}

	// Initialize hash table
	init_hash_table();

	dn result = 0;
	result = delannoy(n, n);

	if(result == DELANNOY_RESULTS[n]) {
		printf("Verification: OK\n");
		return EXIT_SUCCESS;
	}
	printf("Verification: ERR\n");
	return EXIT_FAILURE;
}
