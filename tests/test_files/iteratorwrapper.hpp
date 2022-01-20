#include <vector>
#include <set>

#pragma once

template <typename Iterator, typename Value>
struct IteratorWrapper: public Iterator
{
  typedef Iterator base_iterator;

  IteratorWrapper(): Iterator() {}

  IteratorWrapper(const Iterator & it): Iterator(it) {}
  Value get()
  {
    return *(*this);
  }

  bool operator<(const IteratorWrapper& other) const
  {
    // compare by address of referenced element:
    return &(**this) < &(*other);
  }

  /// Conversion to pointer type for hashing
  operator uintptr_t() const
  {
    return uintptr_t(&(**this));
  }
//  void set(Value v)
//  {
//    *(*this) = v;
//  }
};

// You would probably need to create instances on the cpp side for every boost container that differs in more
// than the Value type. For multiindex this probably means every instance, because you are also specifying
// the members which make up the index.
template <typename Value>
struct CrazyBoostIteratorWrapper: public IteratorWrapper<typename std::set<Value>::iterator, Value> //Note: here the set could be replaced with any weird boost container
{
  CrazyBoostIteratorWrapper(): IteratorWrapper<typename std::set<Value>::iterator, Value>() {}

  //should to be ignored in autowrap
  CrazyBoostIteratorWrapper(const typename IteratorWrapper<typename std::set<Value>::iterator, Value>::base_iterator & it): IteratorWrapper<typename std::set<Value>::iterator, Value>(it) {}
};