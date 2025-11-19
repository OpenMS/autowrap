#include <map>

// A simple wrapper class that can be used as a map key
class Person {
    public:
        int id_;
        Person(): id_(0) { }
        Person(int id): id_(id) { }
        Person(const Person& other): id_(other.id_) { }
        
        // Required for map key
        bool operator<(const Person& other) const {
            return id_ < other.id_;
        }
};

// A simple wrapper class that can be used as a map value
class Score {
    public:
        int value_;
        Score(): value_(0) { }
        Score(int value): value_(value) { }
        Score(const Score& other): value_(other.value_) { }
};

// Example class that uses maps with wrapped types as keys and values
class ScoreTracker {
    public:
        ScoreTracker() { }
        
        // Returns a map with wrapped type as key only
        std::map<Person, int> get_person_scores() {
            std::map<Person, int> scores;
            scores[Person(1)] = 100;
            scores[Person(2)] = 95;
            return scores;
        }
        
        // Returns a map with wrapped type as value only
        std::map<int, Score> get_id_scores() {
            std::map<int, Score> scores;
            scores[1] = Score(100);
            scores[2] = Score(95);
            return scores;
        }
        
        // Returns a map with wrapped types as both key and value
        std::map<Person, Score> get_full_scores() {
            std::map<Person, Score> scores;
            scores[Person(1)] = Score(100);
            scores[Person(2)] = Score(95);
            return scores;
        }
        
        // Takes a map with wrapped types as both key and value
        int sum_scores(std::map<Person, Score>& scores) {
            int sum = 0;
            for (auto& pair : scores) {
                sum += pair.second.value_;
            }
            return sum;
        }
};
