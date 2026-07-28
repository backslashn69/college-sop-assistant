import 'package:flutter/material.dart';
import 'package:college_sop_assistant/features/chat/models/chat_message.dart';
import 'package:college_sop_assistant/features/chat/widgets/chat_bubble.dart';

class ChatScreen extends StatelessWidget {
  const ChatScreen({super.key});

  @override
  Widget build(BuildContext context) {

    final messages = [
  ChatMessage(
    text: "How do I process a transcript request?",
    isUser: true,
  ),
  ChatMessage(
    text:
        "Step 1: Verify the student's identity.\n\n"
        "Step 2: Check for financial holds.\n\n"
        "Step 3: Generate the transcript.\n\n"
        "Step 4: Record the request in the Student Information System.",
    isUser: false,
    source: "Registrar SOP v3.2 • Section 4.1 • Page 18",
  ),
];
    return Scaffold(
      appBar: AppBar(
        title: const Text("YWCC SOP Assistant"),
      ),
      body: Column(
        children: [
          Expanded(
            child: ListView(
              padding: const EdgeInsets.all(16),
              children: messages.map((message) {
                return ChatBubble(message: message);
              }).toList(),
            ),
          ),


          const Divider(height: 1),

          Padding(
            padding: const EdgeInsets.all(12),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    decoration: InputDecoration(
                      hintText: "Ask an SOP question...",
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                  ),
                ),

                const SizedBox(width: 10),

                FilledButton.icon(
                  onPressed: () {},
                  icon: const Icon(Icons.send),
                  label: const Text("Send"),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}