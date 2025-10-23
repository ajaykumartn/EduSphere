import sqlite3
import json

def populate_test_series():
    conn = sqlite3.connect('edusphere.db')
    cursor = conn.cursor()
    
    # JEE Main Test Series Data
    jee_test_series = [
        {
            'title': 'JEE Main Mathematics Mock Test 1',
            'description': 'Comprehensive test covering Algebra, Calculus, and Coordinate Geometry',
            'exam_type': 'JEE Main',
            'subject': 'Mathematics',
            'difficulty_level': 'Medium',
            'duration_minutes': 180,
            'total_marks': 100,
            'questions': [
                {
                    'question_text': 'If the roots of the equation x² - 3x + 2 = 0 are α and β, then the value of α² + β² is:',
                    'option_a': '5',
                    'option_b': '7',
                    'option_c': '9',
                    'option_d': '13',
                    'correct_answer': 'A',
                    'explanation': 'Using Vieta\'s formulas: α + β = 3, αβ = 2. Therefore, α² + β² = (α + β)² - 2αβ = 9 - 4 = 5',
                    'marks': 4,
                    'negative_marks': -1
                },
                {
                    'question_text': 'The derivative of f(x) = x³ - 3x² + 2x - 1 at x = 2 is:',
                    'option_a': '2',
                    'option_b': '4',
                    'option_c': '6',
                    'option_d': '8',
                    'correct_answer': 'A',
                    'explanation': 'f\'(x) = 3x² - 6x + 2. At x = 2: f\'(2) = 3(4) - 6(2) + 2 = 12 - 12 + 2 = 2',
                    'marks': 4,
                    'negative_marks': -1
                },
                {
                    'question_text': 'The area of the triangle with vertices at (0,0), (3,0), and (0,4) is:',
                    'option_a': '6 square units',
                    'option_b': '12 square units',
                    'option_c': '24 square units',
                    'option_d': '8 square units',
                    'correct_answer': 'A',
                    'explanation': 'Area = (1/2) × base × height = (1/2) × 3 × 4 = 6 square units',
                    'marks': 4,
                    'negative_marks': -1
                },
                {
                    'question_text': 'If log₂(x) = 3, then x equals:',
                    'option_a': '6',
                    'option_b': '8',
                    'option_c': '9',
                    'option_d': '12',
                    'correct_answer': 'B',
                    'explanation': 'log₂(x) = 3 means 2³ = x, therefore x = 8',
                    'marks': 4,
                    'negative_marks': -1
                },
                {
                    'question_text': 'The sum of the first 10 terms of the arithmetic progression 2, 5, 8, 11, ... is:',
                    'option_a': '155',
                    'option_b': '145',
                    'option_c': '165',
                    'option_d': '175',
                    'correct_answer': 'A',
                    'explanation': 'First term a = 2, common difference d = 3. Sum = n/2[2a + (n-1)d] = 10/2[4 + 9×3] = 5[4 + 27] = 155',
                    'marks': 4,
                    'negative_marks': -1
                }
            ]
        },
        {
            'title': 'JEE Main Physics Mock Test 1',
            'description': 'Test covering Mechanics, Thermodynamics, and Electromagnetism',
            'exam_type': 'JEE Main',
            'subject': 'Physics',
            'difficulty_level': 'Medium',
            'duration_minutes': 180,
            'total_marks': 100,
            'questions': [
                {
                    'question_text': 'A body of mass 2 kg is moving with velocity 10 m/s. Its kinetic energy is:',
                    'option_a': '50 J',
                    'option_b': '100 J',
                    'option_c': '200 J',
                    'option_d': '400 J',
                    'correct_answer': 'B',
                    'explanation': 'Kinetic Energy = (1/2)mv² = (1/2) × 2 × 10² = 100 J',
                    'marks': 4,
                    'negative_marks': -1
                },
                {
                    'question_text': 'The SI unit of electric field is:',
                    'option_a': 'N/C',
                    'option_b': 'V/m',
                    'option_c': 'Both A and B',
                    'option_d': 'J/C',
                    'correct_answer': 'C',
                    'explanation': 'Electric field can be expressed as N/C (force per unit charge) or V/m (voltage per unit distance). Both are equivalent.',
                    'marks': 4,
                    'negative_marks': -1
                },
                {
                    'question_text': 'The frequency of a wave with wavelength 2 m and speed 340 m/s is:',
                    'option_a': '170 Hz',
                    'option_b': '680 Hz',
                    'option_c': '85 Hz',
                    'option_d': '340 Hz',
                    'correct_answer': 'A',
                    'explanation': 'Frequency = Speed/Wavelength = 340/2 = 170 Hz',
                    'marks': 4,
                    'negative_marks': -1
                },
                {
                    'question_text': 'The work done by a conservative force in a closed path is:',
                    'option_a': 'Maximum',
                    'option_b': 'Minimum',
                    'option_c': 'Zero',
                    'option_d': 'Depends on path',
                    'correct_answer': 'C',
                    'explanation': 'By definition, work done by conservative forces in a closed path is always zero.',
                    'marks': 4,
                    'negative_marks': -1
                },
                {
                    'question_text': 'The escape velocity from Earth\'s surface is approximately:',
                    'option_a': '7.9 km/s',
                    'option_b': '11.2 km/s',
                    'option_c': '15.0 km/s',
                    'option_d': '9.8 km/s',
                    'correct_answer': 'B',
                    'explanation': 'Escape velocity from Earth is approximately 11.2 km/s, calculated using v = √(2GM/R)',
                    'marks': 4,
                    'negative_marks': -1
                }
            ]
        },
        {
            'title': 'JEE Main Chemistry Mock Test 1',
            'description': 'Test covering Organic, Inorganic, and Physical Chemistry',
            'exam_type': 'JEE Main',
            'subject': 'Chemistry',
            'difficulty_level': 'Medium',
            'duration_minutes': 180,
            'total_marks': 100,
            'questions': [
                {
                    'question_text': 'The molecular formula of benzene is:',
                    'option_a': 'C₆H₆',
                    'option_b': 'C₆H₁₂',
                    'option_c': 'C₆H₁₄',
                    'option_d': 'C₆H₁₀',
                    'correct_answer': 'A',
                    'explanation': 'Benzene has the molecular formula C₆H₆ with a ring structure.',
                    'marks': 4,
                    'negative_marks': -1
                },
                {
                    'question_text': 'The pH of a 0.01 M HCl solution is:',
                    'option_a': '1',
                    'option_b': '2',
                    'option_c': '3',
                    'option_d': '0.01',
                    'correct_answer': 'B',
                    'explanation': 'pH = -log[H⁺] = -log(0.01) = -log(10⁻²) = 2',
                    'marks': 4,
                    'negative_marks': -1
                },
                {
                    'question_text': 'The number of electrons in Cl⁻ ion is:',
                    'option_a': '17',
                    'option_b': '18',
                    'option_c': '16',
                    'option_d': '35',
                    'correct_answer': 'B',
                    'explanation': 'Chlorine has 17 electrons. Cl⁻ ion has gained one electron, so total = 17 + 1 = 18 electrons.',
                    'marks': 4,
                    'negative_marks': -1
                },
                {
                    'question_text': 'Which of the following is a noble gas?',
                    'option_a': 'Nitrogen',
                    'option_b': 'Oxygen',
                    'option_c': 'Argon',
                    'option_d': 'Chlorine',
                    'correct_answer': 'C',
                    'explanation': 'Argon (Ar) is a noble gas in Group 18 of the periodic table.',
                    'marks': 4,
                    'negative_marks': -1
                },
                {
                    'question_text': 'The hybridization of carbon in methane (CH₄) is:',
                    'option_a': 'sp',
                    'option_b': 'sp²',
                    'option_c': 'sp³',
                    'option_d': 'sp³d',
                    'correct_answer': 'C',
                    'explanation': 'In methane, carbon forms 4 sigma bonds, requiring sp³ hybridization.',
                    'marks': 4,
                    'negative_marks': -1
                }
            ]
        }
    ]
    
    # NEET Test Series Data
    neet_test_series = [
        {
            'title': 'NEET Biology Mock Test 1',
            'description': 'Comprehensive test covering Botany and Zoology',
            'exam_type': 'NEET',
            'subject': 'Biology',
            'difficulty_level': 'Medium',
            'duration_minutes': 180,
            'total_marks': 180,
            'questions': [
                {
                    'question_text': 'The powerhouse of the cell is:',
                    'option_a': 'Nucleus',
                    'option_b': 'Mitochondria',
                    'option_c': 'Ribosome',
                    'option_d': 'Golgi apparatus',
                    'correct_answer': 'B',
                    'explanation': 'Mitochondria are called the powerhouse of the cell because they produce ATP through cellular respiration.',
                    'marks': 4,
                    'negative_marks': -1
                },
                {
                    'question_text': 'Photosynthesis occurs in:',
                    'option_a': 'Mitochondria',
                    'option_b': 'Nucleus',
                    'option_c': 'Chloroplasts',
                    'option_d': 'Ribosomes',
                    'correct_answer': 'C',
                    'explanation': 'Photosynthesis occurs in chloroplasts, which contain chlorophyll.',
                    'marks': 4,
                    'negative_marks': -1
                },
                {
                    'question_text': 'The basic unit of heredity is:',
                    'option_a': 'Chromosome',
                    'option_b': 'Gene',
                    'option_c': 'DNA',
                    'option_d': 'RNA',
                    'correct_answer': 'B',
                    'explanation': 'A gene is the basic unit of heredity that carries genetic information.',
                    'marks': 4,
                    'negative_marks': -1
                },
                {
                    'question_text': 'Which blood group is called universal donor?',
                    'option_a': 'A',
                    'option_b': 'B',
                    'option_c': 'AB',
                    'option_d': 'O',
                    'correct_answer': 'D',
                    'explanation': 'Blood group O is called universal donor because it has no A or B antigens.',
                    'marks': 4,
                    'negative_marks': -1
                },
                {
                    'question_text': 'The process of cell division that produces gametes is:',
                    'option_a': 'Mitosis',
                    'option_b': 'Meiosis',
                    'option_c': 'Binary fission',
                    'option_d': 'Budding',
                    'correct_answer': 'B',
                    'explanation': 'Meiosis is the process that produces gametes (sex cells) with half the chromosome number.',
                    'marks': 4,
                    'negative_marks': -1
                }
            ]
        }
    ]
    
    # CAT Test Series Data
    cat_test_series = [
        {
            'title': 'CAT Quantitative Aptitude Mock Test 1',
            'description': 'Test covering Arithmetic, Algebra, and Geometry',
            'exam_type': 'CAT',
            'subject': 'Quantitative',
            'difficulty_level': 'Hard',
            'duration_minutes': 60,
            'total_marks': 66,
            'questions': [
                {
                    'question_text': 'If 20% of A = 30% of B, then A:B is:',
                    'option_a': '2:3',
                    'option_b': '3:2',
                    'option_c': '4:5',
                    'option_d': '5:4',
                    'correct_answer': 'B',
                    'explanation': '20% of A = 30% of B → 0.2A = 0.3B → A/B = 0.3/0.2 = 3/2 → A:B = 3:2',
                    'marks': 3,
                    'negative_marks': -1
                },
                {
                    'question_text': 'A train 100m long crosses a platform 200m long in 15 seconds. The speed of the train is:',
                    'option_a': '72 km/hr',
                    'option_b': '60 km/hr',
                    'option_c': '54 km/hr',
                    'option_d': '48 km/hr',
                    'correct_answer': 'A',
                    'explanation': 'Total distance = 100 + 200 = 300m. Speed = 300/15 = 20 m/s = 20 × 3.6 = 72 km/hr',
                    'marks': 3,
                    'negative_marks': -1
                },
                {
                    'question_text': 'The compound interest on Rs. 1000 for 2 years at 10% per annum is:',
                    'option_a': 'Rs. 200',
                    'option_b': 'Rs. 210',
                    'option_c': 'Rs. 220',
                    'option_d': 'Rs. 230',
                    'correct_answer': 'B',
                    'explanation': 'CI = P(1+r/100)ⁿ - P = 1000(1.1)² - 1000 = 1210 - 1000 = Rs. 210',
                    'marks': 3,
                    'negative_marks': -1
                },
                {
                    'question_text': 'If x + 1/x = 5, then x² + 1/x² equals:',
                    'option_a': '23',
                    'option_b': '25',
                    'option_c': '27',
                    'option_d': '29',
                    'correct_answer': 'A',
                    'explanation': 'x² + 1/x² = (x + 1/x)² - 2 = 5² - 2 = 25 - 2 = 23',
                    'marks': 3,
                    'negative_marks': -1
                },
                {
                    'question_text': 'The average of 5 consecutive odd numbers is 15. The largest number is:',
                    'option_a': '17',
                    'option_b': '19',
                    'option_c': '21',
                    'option_d': '23',
                    'correct_answer': 'B',
                    'explanation': 'If average is 15, middle number is 15. Numbers are 11, 13, 15, 17, 19. Largest is 19.',
                    'marks': 3,
                    'negative_marks': -1
                }
            ]
        },
        {
            'title': 'CAT Verbal Ability Mock Test 1',
            'description': 'Test covering Reading Comprehension and Verbal Reasoning',
            'exam_type': 'CAT',
            'subject': 'Verbal',
            'difficulty_level': 'Hard',
            'duration_minutes': 60,
            'total_marks': 66,
            'questions': [
                {
                    'question_text': 'Choose the word that is most similar in meaning to "UBIQUITOUS":',
                    'option_a': 'Rare',
                    'option_b': 'Omnipresent',
                    'option_c': 'Unique',
                    'option_d': 'Temporary',
                    'correct_answer': 'B',
                    'explanation': 'Ubiquitous means present everywhere, which is synonymous with omnipresent.',
                    'marks': 3,
                    'negative_marks': -1
                },
                {
                    'question_text': 'Complete the analogy: BOOK : LIBRARY :: ?',
                    'option_a': 'Car : Garage',
                    'option_b': 'Food : Kitchen',
                    'option_c': 'Medicine : Hospital',
                    'option_d': 'All of the above',
                    'correct_answer': 'D',
                    'explanation': 'All options show the relationship between an item and its storage/usage place.',
                    'marks': 3,
                    'negative_marks': -1
                },
                {
                    'question_text': 'Identify the grammatically correct sentence:',
                    'option_a': 'Neither of the boys were present.',
                    'option_b': 'Neither of the boys was present.',
                    'option_c': 'Neither of the boy were present.',
                    'option_d': 'Neither of the boy was present.',
                    'correct_answer': 'B',
                    'explanation': '"Neither" is singular, so it takes a singular verb "was".',
                    'marks': 3,
                    'negative_marks': -1
                },
                {
                    'question_text': 'Choose the antonym of "EPHEMERAL":',
                    'option_a': 'Temporary',
                    'option_b': 'Brief',
                    'option_c': 'Permanent',
                    'option_d': 'Fleeting',
                    'correct_answer': 'C',
                    'explanation': 'Ephemeral means short-lived or temporary, so its antonym is permanent.',
                    'marks': 3,
                    'negative_marks': -1
                },
                {
                    'question_text': 'Fill in the blank: "The new policy will _____ significant changes in the organization."',
                    'option_a': 'bring about',
                    'option_b': 'bring up',
                    'option_c': 'bring in',
                    'option_d': 'bring down',
                    'correct_answer': 'A',
                    'explanation': '"Bring about" means to cause or result in, which fits the context.',
                    'marks': 3,
                    'negative_marks': -1
                }
            ]
        }
    ]
    
    # UPSC Test Series Data
    upsc_test_series = [
        {
            'title': 'UPSC General Studies Paper 1 Mock Test',
            'description': 'Test covering History, Geography, Polity, and Economics',
            'exam_type': 'UPSC',
            'subject': 'General Studies',
            'difficulty_level': 'Hard',
            'duration_minutes': 120,
            'total_marks': 200,
            'questions': [
                {
                    'question_text': 'The Indian National Congress was founded in:',
                    'option_a': '1885',
                    'option_b': '1875',
                    'option_c': '1895',
                    'option_d': '1905',
                    'correct_answer': 'A',
                    'explanation': 'The Indian National Congress was founded by A.O. Hume in 1885.',
                    'marks': 2,
                    'negative_marks': 0
                },
                {
                    'question_text': 'Which article of the Indian Constitution deals with Right to Education?',
                    'option_a': 'Article 19',
                    'option_b': 'Article 21A',
                    'option_c': 'Article 25',
                    'option_d': 'Article 32',
                    'correct_answer': 'B',
                    'explanation': 'Article 21A provides free and compulsory education to children aged 6-14 years.',
                    'marks': 2,
                    'negative_marks': 0
                },
                {
                    'question_text': 'The Tropic of Cancer passes through how many Indian states?',
                    'option_a': '6',
                    'option_b': '7',
                    'option_c': '8',
                    'option_d': '9',
                    'correct_answer': 'C',
                    'explanation': 'The Tropic of Cancer passes through 8 Indian states: Gujarat, Rajasthan, MP, Chhattisgarh, Jharkhand, West Bengal, Tripura, and Mizoram.',
                    'marks': 2,
                    'negative_marks': 0
                },
                {
                    'question_text': 'Who is known as the "Father of Indian Economics"?',
                    'option_a': 'Dadabhai Naoroji',
                    'option_b': 'M.G. Ranade',
                    'option_c': 'R.C. Dutt',
                    'option_d': 'Gopal Krishna Gokhale',
                    'correct_answer': 'A',
                    'explanation': 'Dadabhai Naoroji is known as the "Father of Indian Economics" for his economic theories and drain of wealth theory.',
                    'marks': 2,
                    'negative_marks': 0
                },
                {
                    'question_text': 'The headquarters of the International Court of Justice is located in:',
                    'option_a': 'Geneva',
                    'option_b': 'New York',
                    'option_c': 'The Hague',
                    'option_d': 'Vienna',
                    'correct_answer': 'C',
                    'explanation': 'The International Court of Justice is headquartered in The Hague, Netherlands.',
                    'marks': 2,
                    'negative_marks': 0
                }
            ]
        }
    ]
    
    # Insert all test series
    all_test_series = jee_test_series + neet_test_series + cat_test_series + upsc_test_series
    
    for test_series in all_test_series:
        # Insert test series
        cursor.execute('''
            INSERT INTO test_series (title, description, exam_type, subject, difficulty_level, duration_minutes, total_marks)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            test_series['title'],
            test_series['description'],
            test_series['exam_type'],
            test_series['subject'],
            test_series['difficulty_level'],
            test_series['duration_minutes'],
            test_series['total_marks']
        ))
        
        test_series_id = cursor.lastrowid
        
        # Insert questions for this test series
        for question in test_series['questions']:
            cursor.execute('''
                INSERT INTO questions (test_series_id, question_text, option_a, option_b, option_c, option_d, 
                                     correct_answer, explanation, marks, negative_marks)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                test_series_id,
                question['question_text'],
                question['option_a'],
                question['option_b'],
                question['option_c'],
                question['option_d'],
                question['correct_answer'],
                question['explanation'],
                question['marks'],
                question['negative_marks']
            ))
    
    conn.commit()
    conn.close()
    print("✅ Test series data populated successfully!")
    print(f"📊 Added {len(all_test_series)} test series with comprehensive questions")

if __name__ == '__main__':
    populate_test_series()