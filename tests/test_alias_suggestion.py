from obsidian_llm.alias_suggester import generate_alias_suggestions


test_title = "deep neural networks"
try:
    aliases = generate_alias_suggestions(test_title)
    print("Generated Aliases:", aliases)
except Exception as e:
    print(f"An error occurred while generating alias suggestions: {e}")
    import traceback

    traceback.print_exc()
