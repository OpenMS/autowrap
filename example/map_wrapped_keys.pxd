# cython: language_level=2
from libcpp.map cimport map as libcpp_map

cdef extern from "map_wrapped_keys.hpp":
    
    cdef cppclass Person:
        # wrap-doc:
        #   A person with an ID that can be used as a map key
        int id_
        Person()
        Person(int id)
        Person(Person&)
    
    cdef cppclass Score:
        # wrap-doc:
        #   A score value
        int value_
        Score()
        Score(int value)
        Score(Score&)
    
    cdef cppclass ScoreTracker:
        # wrap-doc:
        #   Tracks scores for people using maps with wrapped types
        
        ScoreTracker()
        
        libcpp_map[Person, int] get_person_scores()
        # wrap-doc:
        #   Get scores with Person as key (wrapped type) and int as value
        
        libcpp_map[int, Score] get_id_scores()
        # wrap-doc:
        #   Get scores with int as key and Score as value (wrapped type)
        
        libcpp_map[Person, Score] get_full_scores()
        # wrap-doc:
        #   Get scores with both Person (wrapped type) as key and Score (wrapped type) as value
        
        int sum_scores(libcpp_map[Person, Score]& scores)
        # wrap-doc:
        #   Sum all scores from a map with wrapped types as both key and value
