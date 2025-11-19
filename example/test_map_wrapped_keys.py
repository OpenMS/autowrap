#!/usr/bin/env python
"""
Example demonstrating std::map wrapping with wrapped types as keys and/or values.

This example shows that autowrap can now handle:
1. Maps with wrapped types as keys (e.g., std::map<Person, int>)
2. Maps with wrapped types as values (e.g., std::map<int, Score>)
3. Maps with wrapped types as both keys and values (e.g., std::map<Person, Score>)
"""

import os
import sys
import tempfile
import shutil

# Add autowrap to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import autowrap

def main():
    """Generate and build the example."""
    
    # Get the directory of this script
    example_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Create a temporary directory for build
    with tempfile.TemporaryDirectory() as tmpdir:
        print(f"Building example in {tmpdir}...")
        
        # Generate the wrapper code
        pxd_file = os.path.join(example_dir, 'map_wrapped_keys.pxd')
        target_pyx = os.path.join(tmpdir, 'map_wrapped_keys.pyx')
        
        print(f"Generating code from {pxd_file}...")
        include_dirs = autowrap.parse_and_generate_code(
            ['map_wrapped_keys.pxd'], 
            root=example_dir, 
            target=target_pyx, 
            debug=True
        )
        
        # Copy the generated files to show them
        output_dir = os.path.join(example_dir, 'generated')
        os.makedirs(output_dir, exist_ok=True)
        
        for f in os.listdir(tmpdir):
            if f.endswith('.pyx') or f.endswith('.pxd'):
                src = os.path.join(tmpdir, f)
                dst = os.path.join(output_dir, f)
                shutil.copy2(src, dst)
                print(f"Generated: {f}")
        
        print("\n" + "="*70)
        print("Code generation successful!")
        print(f"Generated files are in: {output_dir}")
        print("="*70)
        
        print("\nExample usage would look like:")
        print("""
    import map_wrapped_keys
    
    # Create tracker
    tracker = map_wrapped_keys.ScoreTracker()
    
    # Get map with wrapped key (Person) and simple value (int)
    person_scores = tracker.get_person_scores()
    for person, score in person_scores.items():
        print(f"Person {person.id_} has score {score}")
    
    # Get map with simple key (int) and wrapped value (Score)
    id_scores = tracker.get_id_scores()
    for id, score in id_scores.items():
        print(f"ID {id} has score {score.value_}")
    
    # Get map with both wrapped key and wrapped value
    full_scores = tracker.get_full_scores()
    for person, score in full_scores.items():
        print(f"Person {person.id_} has score {score.value_}")
    
    # Create a new map and pass it to a function
    person1 = map_wrapped_keys.Person(10)
    person2 = map_wrapped_keys.Person(20)
    score1 = map_wrapped_keys.Score(85)
    score2 = map_wrapped_keys.Score(90)
    
    scores = {person1: score1, person2: score2}
    total = tracker.sum_scores(scores)
    print(f"Total score: {total}")  # Should print 175
        """)

if __name__ == '__main__':
    main()
