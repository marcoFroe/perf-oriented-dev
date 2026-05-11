#include <cstddef>
#include <cstring>
#define DEFAULTSIZE 10

template<size_t StorageSize>


class ArrayList{
    public:
        ArrayList();
        ~ArrayList();
        void* insert(size_t index, int value);
        void remove(size_t index);
        void* read(size_t index);
        void write(size_t index, int value);

    private:
        void* storage;
        size_t element_count;
    };
