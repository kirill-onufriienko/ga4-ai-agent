from dotenv import load_dotenv
load_dotenv()

from agent.agent import GA4Agent


def main():
    print("=" * 50)
    print("GA4 AI Agent")
    print("Type 'exit' to quit")
    print("=" * 50)

    agent = GA4Agent()

    while True:
        print()
        user_input = input("You: ").strip()

        if not user_input:
            continue

        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break

        answer = agent.run(user_input)
        print(f"\nAgent: {answer}")
        print("\n" + "-" * 50)


if __name__ == "__main__":
    main()