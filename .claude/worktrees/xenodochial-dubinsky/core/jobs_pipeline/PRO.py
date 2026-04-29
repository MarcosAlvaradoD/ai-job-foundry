def update_cv_descriptor(cv_file, fit_data):
    keywords_highfit = extract_keywords(fit_data, threshold=80)
    with open(cv_file, "a", encoding="utf-8") as f:
        f.write("\n# Aprendizaje Automático\n")
        f.write("Se detectó alto Fit en roles con: " + ", ".join(keywords_highfit))
