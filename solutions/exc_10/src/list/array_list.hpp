#include "list_base.hpp"
#include <cstddef>
#include <vector>

template <size_t StorageSize> class ArrayList : public ListBase {
  public:
	~ArrayList() = default;
	void* insert(size_t index, void* value) override;
	void remove(size_t index) override;
	void* read(size_t index) override;
	void write(size_t index, void* value) override;
	size_t get_element_size() const override { return StorageSize; }

  private:
	std::vector<char> storage;
};