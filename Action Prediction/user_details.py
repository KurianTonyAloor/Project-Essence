import os
from datetime import datetime, timedelta

class UserDetails:
    def __init__(self, user_id):
        self.details = []
        self.index = {}
        self.user_file = f"user{user_id}.txt"
        self.load_from_file()

    def add_detail(self, detail, topics, time):
        entry = {"detail": detail, "topics": topics, "time": time}
        self.details.append(entry)
        for topic in topics:
            if topic not in self.index:
                self.index[topic] = []
            self.index[topic].append(entry)
        with open(self.user_file, "a") as f:
            f.write(f"Detail: {detail}, Topics: {topics}, Time: {time}\n")

    def load_from_file(self):
        if os.path.exists(self.user_file):
            print(f"Loading data from {self.user_file}...")
            with open(self.user_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        detail_part = line.split(", Topics: ")[0].split("Detail: ")[1]
                        topics_part = line.split(", Topics: ")[1].split(", Time: ")[0]
                        time_part = line.split(", Time: ")[1]
                        detail = detail_part
                        topics = eval(topics_part)
                        time = time_part
                        entry = {"detail": detail, "topics": topics, "time": time}
                        self.details.append(entry)
                        for topic in topics:
                            if topic not in self.index:
                                self.index[topic] = []
                            self.index[topic].append(entry)
        else:
            print(f"Creating new log file: {self.user_file}")

    def get_details_by_topic(self, topic):
        return [entry["detail"] for entry in self.index.get(topic, [])]

    def generate_insights(self):
        insights = {}
        for topic, entries in self.index.items():
            insights[topic] = len(entries)
        return insights

    def display_sequential(self):
        if not self.details:
            print("No memories found.")
        for entry in self.details:
            print(f"Detail: {entry['detail']}, Topics: {entry['topics']}, Time: {entry['time']}")

    def predict_next_action_at_time(self, input_time):
        insights = self.generate_insights()
        if not insights:
            return "No data to predict."
        
        input_time = datetime.strptime(input_time, "%H:%M")
        time_range_start = input_time - timedelta(hours=1)
        time_range_end = input_time + timedelta(hours=1)
        time_based_entries = []
        
        for entry in self.details:
            entry_time = datetime.strptime(entry['time'], "%H:%M")
            if time_range_start <= entry_time <= time_range_end:
                time_based_entries.extend(entry['topics'])
        
        time_based_insights = {}
        for topic in time_based_entries:
            if topic not in time_based_insights:
                time_based_insights[topic] = 0
            time_based_insights[topic] += 1
        
        if not time_based_insights:
            return "No frequent actions found around this time."
        
        most_frequent_domain = max(time_based_insights, key=time_based_insights.get)
        return (f"Predicted next action at {input_time.strftime('%H:%M')} "
                f"based on the frequent domain '{most_frequent_domain}' "
                f"which appeared {time_based_insights[most_frequent_domain]} times around this time period.")

def get_next_user_id():
    user_id = 1
    while os.path.exists(f"user{user_id}.txt"):
        user_id += 1
    return user_id

def main():
    print("Welcome! Do you want to load an existing user or create a new one?")
    choice = input("Enter 'load' to load a user or 'new' to create a new user: ").strip().lower()

    if choice == "new":
        user_id = get_next_user_id()
        user_data = UserDetails(user_id)
        print(f"New user created: user{user_id}")
    elif choice == "load":
        user_id = int(input("Enter the user ID to load (e.g., '1' for user1): "))
        if os.path.exists(f"user{user_id}.txt"):
            user_data = UserDetails(user_id)
        else:
            print(f"No log file found for user{user_id}.")
            return
    else:
        print("Invalid choice. Exiting...")
        return

    while True:
        print("\nOptions: 1. Memory so far, 2. Details on a specific topic, 3. Add details, 4. Generate insights, 5. Predict next action, 6. Predict next action at a specific time, 7. Exit")
        ch = int(input("Enter your choice: "))

        if ch == 1:
            user_data.display_sequential()

        elif ch == 2:
            topic = input("Enter the topic: ")
            details = user_data.get_details_by_topic(topic)
            print(f"Details related to {topic}: {details}")

        elif ch == 3:
            detail = input("Enter the detail: ")
            topics = input("Enter the topics (comma-separated): ").split(",")
            time = input("Enter the time in HH:MM format: ")
            user_data.add_detail(detail, [topic.strip() for topic in topics], time)
            print("Detail added successfully.")

        elif ch == 4:
            insights = user_data.generate_insights()
            print("Insights generated:", insights)

        elif ch == 5:
            user_data.predict_next_action()

        elif ch == 6:
            input_time = input("Enter the time (HH:MM format) for prediction: ")
            user_data.predict_next_action_at_time(input_time)

        elif ch == 7:
            print("Exiting...")
            break

        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()


    
    
