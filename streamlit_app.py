from dotenv import load_dotenv
import os
import anthropic
import streamlit as st

# Load environment variables
load_dotenv()
api_key = os.getenv("ANTHROPIC_API_KEY")

# Verify API key
if not api_key:
    st.error("API key not found. Please check your .env file.")
    st.stop()

# Instantiate the Anthropic client
client = anthropic.Anthropic(api_key=api_key)

def is_incomplete(response_text):
    """
    Check if the response appears incomplete based on certain indicators.
    """
    incomplete_indicators = [
        "would you like me to continue",
        "continue with additional frames",
        "continue with remaining frames",
        "let me know if you'd like me to continue"
    ]
    return any(phrase in response_text for phrase in incomplete_indicators)

def get_full_response(unit_info):
    """
    Generate the full video script by chaining API calls if the output is truncated.
    """
    # Define your full prompt
    user_content = f"""
# CONTEXT #
You are a helpful assistant who creates scripts for narrators to read in instructional and educational videos. You also make suggestions for visuals that can accompany the text being read by the narrator.

We are looking to create a video series that helps teachers of our math curriculum better understand the content that they will be teaching in a Unit. We do this by looking deeply at the content of each section in the unit and connecting that with prior learning.

# OBJECTIVE #
I am going to give you the following information in batches:
- Grade Level == {{GRADE}}
- Unit Number == {{UNIT_NUMBER}}
- Unit Name == {{UNIT_NAME}}
- Unit Goals == {{GOALS}} **If available**
- Unit Narrative == {{CURRENT}}
- Vertical Progression == {{VERTICAL}}
- Section Name and Overview (will repeat for all sections in the unit) == {{SECTIONS}}
- Sample Script == {{SCRIPT_SAMPLE}}

I would like you to take the following steps:

>>>STEP 1: Building your knowledge base - Current grade and prior Knowledge
a. Review {{GOALS}} and {{CURRENT}} to understand what is being taught in this unit. 
b. Review {{VERTICAL}} to understand what skills students have learned in previous grades and how they connect to {{GOALS}} and {{CURRENT}}.
c. Write a summary of your understanding citing connections to prior learning as appropriate. == {{SUMMARY_OVERVIEW}}
d. Identify common misconceptions for each section from the vertical progression information. Note these for later use. == {{MISCONCEPTIONS}}
e. Review any tools, manipulatives, or resources mentioned in unit content and note them for reference. == {{TOOLS}}

>>>STEP 2: Deepen your knowledge base - Understanding Section content. 
a. Review {{SECTIONS}} to understand what is being taught in each unit section. 
b. Identify relationships between content presented in each section and draft a short summary of how the ideas in each section connect to work in other sections. == {{SUMMARY_PROG}}
c. Write a short summary for each section explaining how it connects to the larger story of the unit. == {{SUMMARY_SECTION[ ]}}
***Repeat for each section in the unit. Use {{VERTICAL}} and {{SUMMARY_OVERVIEW}} to make connections to prior learning as appropriate.
d. For each section, tie relevant misconceptions from {{MISCONCEPTIONS}} to the content and skills being taught. Note how prior learning can help address these misconceptions. == {{MISCONCEPTIONS_MAP}}
e. Identify where in each section specific tools from {{TOOLS}} are utilized and how they support learning. == {{TOOLS_MAP}}

>>>STEP 3: Script Writing
a. Generate a list of numbered Frames with a bulleted list underneath each. Bullets should outline Narration, On-Screen Text, and Visuals. 
***Use {{SCRIPT_SAMPLE}} as a model for layout and formatting in this process.
b. Use {{SUMMARY_OVERVIEW}} to begin writing a script that will be used to give the audience an overview of the unit’s content. This should explain at a high level the big ideas of the unit, how they will be developed over the sections, and make connections to prior learning. This section of the script should take 3 minutes and be broken out into multiple frames. == {{UNIT_SCRIPT}}
***NOTE: Generate frame breaks in a way that allows new visuals and on-screen text to support the content of the narration. 
c. Write the script for each section in the unit. These scripts should overview the section, review key concepts, connect the ideas to the work of the unit, review any tools or manipulatives used to help with the learning in the section and make connections to prior learning as appropriate. Each section script should take 2 minutes and be broken into frames considering how new visuals and on-screen text support the content of the narration. == {{SECTION_SCRIPT}}
***NOTE: repeat this process for each section in the unit.
f. Write the script for your conclusion to the video. This should restate the grade level, unit number, and name, and restate {{GOALS}} and key idea(s) of the unit before thanking viewers for watching and all that they do for their students. {{CONCLUSION}}
***NOTE: This should be succinct enough to have one section and one visual that solidifies and makes the idea stick.
g. Combine {{UNIT_SCRIPT}}, {{SECTION_SCRIPT}}, and {{CONCLUSION}} to make a first draft of the script. == {{DRAFT_TEXT}}
***NOTE: {{DRAFT_TEXT}} should be formatted in a table and formatted according to step 3.a with Frame # and Narration columns completed
h. When organizing frames for each section, follow this pattern:
- Begin with core content and key understandings
- Include relevant misconceptions and how to address them using prior learning
- Show how tools and representations support learning in this section
- Make explicit connections to unit progression
-- Ensure conclusion frames:
- Come only after all section content is complete
- Bridge to future learning
- Restate key understandings
- Reference available resources

>>>STEP 4: Adding on-screen text and visual descriptions.
a. Review each frame in {{DRAFT_TEXT}} to understand how it relates to {{SUMMARY_OVERVIEW}}
b. For each frame, draft on-screen text that can be displayed during the narration. Consider the ideas in {{REVISON_SAMPLES}} as you think about what to display
***NOTE: This text should be short and concise, displaying the big ideas while the narrator elaborates.
c. Review each frame and determine if a visual could be used to support the narrated text. If so, describe in detail the visuals that should be added. 
***NOTE: Consider any representations, strategies, or tools mentioned in {{CURRENT}} or {{SECTIONS}} to guide your decision-making.
d. Add on-screen text and visual descriptions to the appropriate columns in {{DRAFT_TEXT}} == {{DRAFT}}

>>>STEP 5: Review and Revision
a. Review {{DRAFT}} ensuring content flows as one complete story. Adjust content based on your review before outputting the final version. == {{FINAL}}

# STYLE #
Look to the {{SCRIPT_SAMPLE}} as a sample of the style I would like you to use. 
Each section's frames should form a complete mini-story within the larger unit narrative.
Misconceptions should be addressed in context of the relevant content, not as a separate section.
Tool usage should be integrated into content explanation, not presented separately.
Transitions between sections should emphasize conceptual connections.

# TONE #
Look to the {{SCRIPT_SAMPLE}} as a sample of the tone I would like you to use.

# AUDIENCE #
Teachers and administrators using Kiddom’s math curriculum.

# ORGANIZATION PRINCIPLES #
Follow this hierarchy when structuring frames:
- Unit Introduction & Prior Learning
- For each section:
  -- Core content and skills
  -- Common misconceptions with connections to prior learning
  -- Tools and representations that support learning
  -- Connections to unit progression
- Applications and Real-World Connections
- Concluding Frames:
  -- Broader mathematical connections
  -- Available resources
  -- Thank you

# RESPONSE #

Only display the final version of the video script.
***Use the example below to guide your formatting

>>>EXAMPLE of Frame Formatting

FRAME 1
Narration: "Welcome to Grade 4 Unit 6, where students develop strategies for multi-digit multiplication and division. This unit represents a crucial step in students' mathematical journey, as they move from basic multiplication and division to working with larger numbers systematically. Our goal is to help students build fluency while maintaining strong conceptual understanding."
On-Screen Text: "Grade 4 Unit 6: Multi-Digit Operations"
Visuals: Simple title slide with unit name and key operations (× ÷) in large font, using a clean font like Arial or Roboto
FRAME 2
Narration: "Let's examine how this unit builds on prior learning. In Grade 2, students developed foundational skills by working with equal groups and understanding even and odd numbers. This progressed in Grade 3 to using area models and base-ten diagrams for multiplication, where students learned to decompose two-digit factors into tens and ones. Now in Grade 4, they'll extend these strategies to work with larger numbers."
On-Screen Text: "Building on Prior Knowledge"
Visuals: Three simple boxes in a row connected by arrows: Box 1: "Grade 2: Equal Groups" with simple circles grouped in pairs; Box 2: "Grade 3: Area Models" with a basic rectangular model; Box 3: "Grade 4: Multi-digit Operations" with an example problem
FRAME 3
Narration: "A key understanding from Grade 3 that students bring to this work is that they can find the value of a product by decomposing one factor into smaller parts, finding partial products, and then combining them. This fundamental concept will be essential as they tackle larger numbers in Grade 4."
On-Screen Text: "Key Understanding: Breaking Numbers Apart"
Visuals: Simple example showing 24 × 6 broken into (20 × 6) + (4 × 6) with color-coding to show the relationship between parts
    """

    # Build the initial conversation history with only user messages.
    conversation_history = [
        {"role": "user", "content": user_content + "\n\n" + unit_info}
    ]
    
    full_response = ""
    while True:
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            system="You are a helpful assistant that converts provided unit content into a final version video script according to the instructions.",
            messages=conversation_history,
            max_tokens=1500,  # Increase if needed
            stream=False
        )
        # Assume response.content is a list; take text from the first element.
        chunk = response.content[0].text
        full_response += chunk
        
        # Check if the response appears to be incomplete.
        if not is_incomplete(chunk):
            break
        
        # Append the received chunk and ask for the continuation.
        conversation_history.append({"role": "assistant", "content": chunk})
        conversation_history.append({
            "role": "user",
            "content": "Please continue generating the rest of the video script without asking if you should continue."
        })
    
    return full_response

# Streamlit app UI
st.title("Video Script Generator")
st.subheader("Convert teacher-provided unit content into a final version video script.")

# Create a three-column layout for Grade Level, Unit Number, and Unit Name
col1, col2, col3 = st.columns(3)
with col1:
    grade = st.selectbox(
        "Select Grade Level:",
        [
            "Kindergarten", "Grade 1", "Grade 2", "Grade 3", "Grade 4", 
            "Grade 5", "Grade 6", "Grade 7", "Grade 8", 
            "Algebra 1", "Geometry", "Algebra 2"
        ]
    )
with col2:
    unit_number = st.text_input("Enter Unit Number:")
with col3:
    unit_name = st.text_input("Enter Unit Name:")

# Other input fields
goals = st.text_area("Enter Unit Goals (if available):")
current = st.text_area("Enter Unit Narrative:")
vertical = st.text_area("Enter Vertical Progression:")
sections = st.text_area("Enter Section Name and Overview (for all sections):")

# Load the sample script from file in the reference_materials folder
try:
    with open("reference_materials/Grade 4 Unit 6 Video Script.txt", "r") as file:
        script_sample = file.read()
except Exception as e:
    st.error(f"Could not load sample script file: {e}")
    script_sample = ""

# Combine all the inputs into a single string for substitution
unit_info = f"""
GRADE: {grade}
UNIT_NUMBER: {unit_number}
UNIT_NAME: {unit_name}
GOALS: {goals}
CURRENT: {current}
VERTICAL: {vertical}
SECTIONS: {sections}
SCRIPT_SAMPLE: {script_sample}
"""

# Generate response when button is clicked
if st.button("Generate Video Script"):
    # Check for required fields
    if grade and unit_number and unit_name and current and vertical and sections and script_sample:
        with st.spinner("Generating video script..."):
            try:
                response_text = get_full_response(unit_info)
                st.success("Video Script Generated!")
                st.text_area("Generated Video Script", value=response_text, height=400)
            except Exception as e:
                st.error(f"An error occurred: {e}")
    else:
        st.warning("Please fill in all required fields (Grade Level, Unit Number, Unit Name, Unit Narrative, Vertical Progression, Section Overview) and ensure the sample script file is available in the reference_materials folder.")
