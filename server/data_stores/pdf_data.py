import numpy as np
from server.brain.vector_db import pdf_collection
from weaviate.classes.query import Filter
from sentence_transformers import CrossEncoder
from server.brain.chains import find_chapter_chain

model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L6-v2", max_length=512)

def sigmoid(x):
    return 1 / (1 + np.exp(-x))

def get_pdf_data(question: str, user_course , user_history):
    course_name = fetch_course_name(user_course)
    chapter_name = fetch_chapter_names(question, user_history)
    all_filter = Filter.by_property("course").equal(course_name)
    if chapter_name:
        all_filter = (all_filter & Filter.by_property("chapter").equal(chapter_name))
    # print("Processed Data:", "-"*20, chapter_name, course_name)
    response = pdf_collection.query.hybrid(query=question,
                                           limit=10,
                                           filters=all_filter)
    print("DB Response:", "-"*20, response.objects)
    if not response.objects:
        return ''
    all_documents = [prop.properties.get('document') for prop in response.objects]
    re_ranked = model.rank(query=question, documents=all_documents, top_k=1)
    # print("Ranked value:", '-'*20, re_ranked)
    correct_documents = []
    for doc in re_ranked:
        # print("Sigmoid------->>>>", sigmoid(doc['score']))
        if sigmoid(doc['score']) > 1e-4:
            correct_documents.append(all_documents[doc.get('corpus_id')])
    return "\n".join(correct_documents)

def fetch_course_name(course_name: str) -> str:
    return "plus_two" if course_name == "JEE Repeater 2026" else course_name

def fetch_chapter_names(query: str, user_history) -> str:
    prompt_str = """
                Plus Two -> Physics -> Chapter 1 -> electric_charges_and_fields
                Plus Two -> Physics -> Chapter 2 -> ellectrostatic_potential_and_capacitance
                Plus Two -> Physics -> Chapter 3 -> current_electricity
                Plus Two -> Physics -> Chapter 4 -> moving_charges_and_magnetism
                Plus Two -> Physics -> Chapter 5 -> magnetism_and_matter
                Plus Two -> Physics -> Chapter 6 -> electromagnetic_induction
                Plus Two -> Physics -> Chapter 7 -> alternating_current
                Plus Two -> Physics -> Chapter 8 -> electromagnetic_waves
                Plus Two -> Physics -> Chapter 9 -> ray_optics_and_optical_instruments
                Plus Two -> Physics -> Chapter 10 -> wave_optics
                Plus Two -> Physics -> Chapter 11 -> dual_nature_of_radiation_and_matter
                Plus Two -> Physics -> Chapter 12 -> atoms
                Plus Two -> Physics -> Chapter 13 -> nuclei
                Plus Two -> Physics -> Chapter 14 -> semiconductor_electronics:_materials,_devices_and_simple_circuits
                Plus Two -> Chemistry -> Chapter 1 -> solutions
                Plus Two -> Chemistry -> Chapter 2 -> electrochemistry
                Plus Two -> Chemistry -> Chapter 3 -> chemical_kinetics
                Plus Two -> Chemistry -> Chapter 4 -> the_d-_and_f-_block_elements
                Plus Two -> Chemistry -> Chapter 5 -> coordination_compounds
                Plus Two -> Chemistry -> Chapter 6 -> haloalkanes_and_haloarenes
                Plus Two -> Chemistry -> Chapter 7 -> alcohols,_phenols_and_ethers
                Plus Two -> Chemistry -> Chapter 8 -> aldehydes,_ketones_and_carboxylic_acids
                Plus Two -> Chemistry -> Chapter 9 -> amines
                Plus Two -> Chemistry -> Chapter 10 -> biomolecules
                Plus One -> Physics -> Chapter 4 -> laws_of_motion
                Plus One -> Physics -> Chapter 5 -> work,_energy_and_power
                Plus One -> Physics -> Chapter 6 -> systems_of_particles_and_rotational_motion
                Plus One -> Physics -> Chapter 7 -> gravitation
                Plus One -> Physics -> Chapter 8 -> mechanical_properties_of_solids
                Plus One -> Physics -> Chapter 9 -> mechanical_properties_of_fluids
                Plus One -> Physics -> Chapter 10 -> thermal_properties_of_matter
                Plus One -> Physics -> Chapter 12 -> kinetic_theory
                Plus One -> Physics -> Chapter 13 -> oscillations
                Plus One -> Physics -> Chapter 14 -> waves
                Plus One -> Mathematics -> Chapter 2 -> relations_and_functions
                Plus One -> Mathematics -> Chapter 3 -> trigonometric_functions
                Plus One -> Mathematics -> Chapter 4 -> complex_numbers_and_quadratic_equations
                Plus One -> Mathematics -> Chapter 5 -> linear_inequalities
                Plus One -> Mathematics -> Chapter 6 -> permutations_and_combinations
                Plus One -> Mathematics -> Chapter 7 -> binomial_theorem
                Plus One -> Mathematics -> Chapter 8 -> sequences_and_series
                Plus One -> Mathematics -> Chapter 10 -> conic_sections
                Plus One -> Mathematics -> Chapter 11 -> introduction_to_three_dimensional_geometry
                Plus One -> Mathematics -> Chapter 12 -> limits_and_derivatives
                Plus One -> Mathematics -> Chapter 13 -> statistics
                Plus One -> Mathematics -> Chapter 14 -> probability
                """
    chapter_name = find_chapter_chain.invoke(input={"query":query, "chapter_list":prompt_str, "user_history": user_history})
    return chapter_name if chapter_name.rstrip() != "FALSE" else None