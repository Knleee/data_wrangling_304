import pandas as pd
import plotly.graph_objects as go

def load_and_prepare_data():
    try:
        # Load data files
        pathways = pd.read_csv('/Users/kebbaleigh/Documents/Education/DATA 304/data_wrangling_304/data/assignment_5/raw/course_pathways.csv')
        catalog = pd.read_csv('/Users/kebbaleigh/Documents/Education/DATA 304/data_wrangling_304/data/assignment_5/raw/course_catalog_by_major.csv')
        
        # Clean and normalize data
        pathways['Major'] = pathways['Major'].str.strip().str.lower()
        pathways['Program'] = pathways['Program'].str.strip().str.upper()
        catalog['Major'] = catalog['Major'].str.strip().str.lower()
        catalog['Course'] = catalog['Course'].str.strip()
        catalog['Type'] = catalog['Type'].str.strip().str.lower()

        # Filter to CECS students in target majors
        target_majors = ['data science', 'artificial intelligence', 'cybersecurity']
        pathways = pathways[
            (pathways['Program'] == 'CECS') & 
            (pathways['Major'].isin(target_majors))
        ].copy()

        # Split course paths with multiple separator options
        pathways['Courses'] = pathways['CoursePath'].str.split(r'\s*→\s*|\s*->\s*')

        # Get required courses
        required = catalog[catalog['Type'] == 'required']
        required_dict = required.groupby('Major')['Course'].apply(list).to_dict()

        # Match courses with flexible matching
        def match_courses(row):
            major_courses = required_dict.get(row['Major'], [])
            return [c.strip() for c in row['Courses'] 
                   if any(c.strip().lower() == rc.strip().lower() 
                         for rc in major_courses)]

        pathways['RequiredCourses'] = pathways.apply(match_courses, axis=1)
        
        # Final filtering
        return pathways[pathways['RequiredCourses'].apply(len) >= 2], required_dict

    except Exception as e:
        print(f"Data loading error: {str(e)}")
        return None, None

def create_sankey_diagram(pathways, required_dict):
    """Create interactive Sankey diagram"""
    try:
        # Extract all transitions
        transitions = []
        for path in pathways['RequiredCourses']:
            for i in range(len(path)-1):
                transitions.append({
                    'source': path[i],
                    'target': path[i+1],
                    'major': pathways[pathways['RequiredCourses'].apply(lambda x: path[i] in x)].iloc[0]['Major']
                })
        
        if not transitions:
            print("No valid transitions found")
            return None

        # Create transition counts
        transitions_df = pd.DataFrame(transitions)
        transition_counts = transitions_df.groupby(['source', 'target', 'major']).size().reset_index(name='count')
        
        # Prepare Sankey data
        all_courses = pd.unique(transition_counts[['source', 'target']].values.ravel('K'))
        course_to_id = {course: i for i, course in enumerate(all_courses)}
        
        # Color mapping
        major_colors = {
            'data science': '#1f77b4',
            'artificial intelligence': '#ff7f0e',
            'cybersecurity': '#2ca02c'
        }
        
        # Create Sankey diagram
        fig = go.Figure(go.Sankey(
            arrangement="snap",
            node=dict(
                pad=20,
                thickness=20,
                line=dict(color="black", width=0.5),
                label=all_courses,
                color=[major_colors.get(
                    next((m for m, courses in required_dict.items() 
                         if course in courses), 'gray'), '#d62728') 
                    for course in all_courses]
            ),
            link=dict(
                source=[course_to_id[x] for x in transition_counts['source']],
                target=[course_to_id[x] for x in transition_counts['target']],
                value=transition_counts['count'],
                color=[major_colors[m] for m in transition_counts['major']],
                hovertemplate='%{source.label} → %{target.label}<br>Students: %{value}<extra></extra>'
            )
        ))
        
        fig.update_layout(
            title_text="CECS Program Course Pathways",
            font_size=12,
            height=1000,
            margin=dict(l=100, r=100, b=100, t=100)
        )
        
        return fig
    
    except Exception as e:
        print(f"Visualization error: {str(e)}")
        return None

def main():
    print("=== CECS Pathway Sankey Diagram ===")
    
    # Load and prepare data
    pathways, required_dict = load_and_prepare_data()
    if pathways is None or pathways.empty:
        print("No valid data to visualize")
        return
    
    # Create Sankey diagram
    fig = create_sankey_diagram(pathways, required_dict)
    if fig:
        # Save as HTML (works without Kaleido)
        fig.write_html("cecs_pathways_sankey.html")
        print("Successfully saved as cecs_pathways_sankey.html")
        print("Opening interactive visualization...")
        fig.show()
    else:
        print("Failed to create diagram")

if __name__ == "__main__":
    main()