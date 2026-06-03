#pragma once

#include <cstddef>
#include <vector>
#include "list_base.hpp"

template<size_t StorageSize>
class TieredArray : public ListBase {
  public:
	TieredArray();
	~TieredArray();

	void* insert(size_t index, void* value) override;
	void remove(size_t index) override;
	void* read(size_t index) override;
	void write(size_t index, void* value) override;

	// size in bytes of a single element
	size_t get_element_size() const override { return StorageSize; }

	size_t size() const;

  private:
	static constexpr size_t blockCapacity = 5;

	struct BlockPosition {
		size_t blockIndex;
		size_t offset;
	};

	// store raw bytes: each block holds consecutive elements as bytes
	std::vector<std::vector<char>> blocks;
	size_t elementCount = 0;

	BlockPosition locate(size_t index) const;
	void splitBlock(size_t blockIndex);
};