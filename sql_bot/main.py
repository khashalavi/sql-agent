import traceback
from agent.agent_init import agent

if __name__ == "__main__":
    print("Hello, I am database research AI Agent. Ask me anything related to the databases! (type 'exit' to quit):")
    while True:
        try:
            user_input = input("\n> ")
            if user_input.strip().lower() in {"exit", "quit"}:
                print("Goodbye!")
                break
            result = agent.run(user_input)
            print("\n=== FINAL ANSWER ===")
            print(result)
        except Exception:
            traceback.print_exc()