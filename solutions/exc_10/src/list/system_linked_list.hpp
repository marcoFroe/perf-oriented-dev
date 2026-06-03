#include "list_base.hpp"
#include <cstddef>
#include <cstring>
#include <forward_list>

template <size_t StorageSize> class SystemLinkedList : public ListBase {
  public:
	SystemLinkedList();
	~SystemLinkedList();
	void* insert(size_t index, void* value) override;
	void remove(size_t index) override;
	void* read(size_t index) override;
	void write(size_t index, void* value) override;
	size_t get_element_size() const override { return StorageSize; }

  private:
	struct Node {
		char value[StorageSize];
	};
	std::forward_list<Node> list;
};
