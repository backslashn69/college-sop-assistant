import 'package:flutter/material.dart';
import 'package:college_sop_assistant/features/chat/models/chat_message.dart';
import 'package:college_sop_assistant/features/chat/widgets/chat_bubble.dart';

class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key});

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final TextEditingController _controller = TextEditingController();

  final List<ChatMessage> _messages = [
    ChatMessage(
      text: "How do I process a transcript request?",
      isUser: true,
    ),
    ChatMessage(
      text:
          "Step 1: Verify the student's identity.\n\n"
          "Step 2: Check for financial holds.\n\n"
          "Step 3: Generate the transcript.",
      isUser: false,
      source: "Registrar SOP v3.2 • Section 4.1 • Page 18",
  ),
];
void _sendMessage() {
  final text = _controller.text.trim();

  if (text.isEmpty) return;

  setState(() {
    _messages.add(
      ChatMessage(
        text: text,
        isUser: true,
      ),
    );

    // Temporary AI response
    _messages.add(
      ChatMessage(
        text:
            "I'm not connected to the SOP database yet.\n\n"
            "This is where the AI response will appear.",
        isUser: false,
      ),
    );
  });

  _controller.clear();
}

@override
  Widget build(BuildContext context) { 
    return Scaffold(
      appBar: AppBar(
        title: const Text("YWCC SOP Assistant"),
      ),
      body: Column(
        children: [
          Expanded(
            child: ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: _messages.length,
              itemBuilder: (context, index) {
                return ChatBubble(message: _messages[index]);
              },
            ),
          ),


          const Divider(height: 1),

          Padding(
            padding: const EdgeInsets.all(12),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _controller,
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
                  onPressed: _sendMessage,
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