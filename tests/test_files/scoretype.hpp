#include <vector>
#include <set>
#include <string>
#include "iteratorwrapper.hpp"

//template <typename Iterator, typename Value>
//struct IteratorWrapper: public Iterator
//{
//  IteratorWrapper(): Iterator() {}
//
//  IteratorWrapper(const Iterator & it): Iterator(it) {}
//  Value get()
//  {
//    return *(*this);
//  }
////  void set(Value v)
////  {
////    *(*this) = v;
////  }
//};

/** @brief Information about a score type.
*/
struct ScoreType
{
  bool higher_better;
  std::string name;

  ScoreType():
    higher_better(true), name()
  {
  }

  ScoreType(bool higher_better, std::string myname):
    higher_better(higher_better), name(myname)
  {
  }

  // don't include "higher_better" in the comparison:
  bool operator<(const ScoreType& other) const
  {
    // @TODO: implement/use "CVTerm::operator<"?
    return (std::tie(this->name) <
            std::tie(other.name));
  }

  // don't include "higher_better" in the comparison:
  bool operator==(const ScoreType& other) const
  {
    return this->name == other.name;
  }

  bool isBetterScore(double first, double second) const
  {
    if (higher_better) return first > second;
    return first < second;
  }
};

typedef std::set<ScoreType>::iterator SetIter;
typedef std::set<ScoreType> ScoreTypes;
typedef IteratorWrapper<std::set<ScoreType>::iterator, ScoreType> ScoreTypeRef;
typedef CrazyBoostIteratorWrapper<ScoreType> BoostContainerScoreTypeRef;


struct ProcessingSoftware
{
  ScoreTypes s = {ScoreType(true, "comet"), ScoreType(false, "msgf"), ScoreType(false,"eval")};

  std::vector<ScoreTypeRef> assigned_scores =
    {ScoreTypeRef(s.find(ScoreType(true,"comet"))), ScoreTypeRef(s.find(ScoreType(false,"eval")))};

  std::vector<BoostContainerScoreTypeRef> assigned_scores_boost =
    {
        BoostContainerScoreTypeRef(s.find(ScoreType(true,"comet"))),
        BoostContainerScoreTypeRef(s.find(ScoreType(false,"eval")))
    };
};
