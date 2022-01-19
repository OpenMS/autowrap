#include <vector>
#include <set>

#pragma once

template <typename Iterator, typename Value>
struct IteratorWrapper: public Iterator
{
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

///** @brief Information about a score type.
//*/
//struct ScoreType
//{
//  bool higher_better;
//
//  ScoreType():
//    higher_better(true)
//  {
//  }
//
//  explicit ScoreType(bool higher_better):
//    higher_better(higher_better)
//  {
//  }
//};
//
//typedef std::set<ScoreType>::iterator SetIter;
//typedef std::set<ScoreType> ScoreTypes;
//typedef IteratorWrapper<std::set<ScoreType>::iterator, ScoreType> ScoreTypeRef;
//
//
//struct ProcessingSoftware
//{
//  std::vector<ScoreTypeRef> assigned_scores;
//
//  ScoreTypes s = {ScoreType(true), ScoreType(false), ScoreType()};
//  ScoreTypeRef getFirst()
//  {
//    return s.begin();
//  }
//};
