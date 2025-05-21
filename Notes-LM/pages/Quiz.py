import streamlit as st
if st.session_state.quiz_questions is None:
    st.markdown("""
Enter topics on the main page to begin quiz!""")
else:
    import plotly.express as px

    questions = st.session_state.quiz_questions
    st.session_state.total_questions = len(questions)
    total_questions = st.session_state.total_questions
    st.progress(len(st.session_state.attempted_questions) / total_questions)
    st.write(
        f"Questions attempted: {len(st.session_state.attempted_questions)}/{total_questions}"
    )
        
    # Main quiz interface
    if not st.session_state.quiz_completed:
        if st.session_state.current_question_idx < total_questions:
            current_question = questions[st.session_state.current_question_idx]

            # Display question
            st.markdown(f"### {current_question['question']}")

            # Display extra content if available
            if current_question["extra_content"]:
                con = st.container(border=True)
                con.write(current_question["extra_content"])

            # Display image if available
            if current_question["image_link"]:
                st.markdown(
                    f"""![Photo]({current_question["image_link"]})""",
                    unsafe_allow_html=True,
                )

            # Create two columns for options
            col1, col2 = st.columns(2)

            # Get the options
            options = current_question["options"]
            option_items = list(options.keys())
            st.divider()
            # Display options in columns
            with col1:
                c1 = st.container(border=True)
                c2 = st.container(border=True)
                c1.markdown("A: " + option_items[0])
                c2.markdown("B: " + option_items[1])
            with col2:
                c1 = st.container(border=True)
                c2 = st.container(border=True)
                c1.markdown("C: " + option_items[2])
                c2.markdown("D: " + option_items[3])

            choice = st.radio("Select an option", ["A", "B", "C", "D"])

            if st.button("Next Question"):
                if choice:
                    answer = (
                        option_items[0]
                        if choice == "A"
                        else option_items[1]
                        if choice == "B"
                        else option_items[2]
                        if choice == "C"
                        else option_items[3]
                        if choice == "D"
                        else None
                    )
                    if options[answer]:
                        st.session_state.score += 1
                        st.session_state.attempted_questions.add(
                            st.session_state.current_question_idx
                        )
                    else:
                        st.session_state.attempted_questions.add(
                            st.session_state.current_question_idx
                        )
                    st.session_state.current_question_idx += 1
                st.rerun()

        # Check if quiz is complete
        if st.session_state.current_question_idx >= total_questions:
            st.session_state.quiz_completed = True
            st.rerun()

    # End screen
    if st.session_state.quiz_completed:
        st.header("Quiz Complete! 🎉", divider=True)

        fig = px.pie(
            names=["Correct", "Incorrect"],
            values=[
                st.session_state.score,
                total_questions - st.session_state.score,
            ],
            hole=0.6,
            color_discrete_sequence=["#43E6B5", "#BB054E"],
            title=f"You scored {st.session_state.score} out of {total_questions} questions right!",
        )
        st.plotly_chart(fig)