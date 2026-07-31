import 'package:flutter/material.dart';
import 'package:college_sop_assistant/features/chat/models/chat_message.dart';
import 'package:college_sop_assistant/features/chat/widgets/chat_bubble.dart';
import 'package:college_sop_assistant/features/chat/widgets/typing_indicator.dart';

class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key});

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final TextEditingController _controller = TextEditingController();
  final ScrollController _scrollController = ScrollController();
 
  bool _isTyping = false;

  final List<ChatMessage> _messages = [
    ChatMessage(
      text: 'How do I process a transcript request?',
      isUser: true,
    ),
    ChatMessage(
      text:
          "Step 1: Verify the student's identity.\n\n"
          'Step 2: Check for financial holds.\n\n'
          'Step 3: Generate the transcript.',
      isUser: false,
      source: 'Registrar SOP v3.2 • Section 4.1 • Page 18',
    ),
  ];

  Future<void> _sendMessage() async {
    final text = _controller.text.trim();

    if (text.isEmpty || _isTyping) {
      return;
    }

  setState(() {
    _messages.add(
      ChatMessage(
        text: text,
        isUser: true,
      ),
    );

  });

  _controller.clear();
  _scrollToBottom();

  await WidgetsBinding.instance.endOfFrame;

  await Future<void>.delayed(
    const Duration(milliseconds: 300),
  );

  if (!mounted) {
    return;
  }

  setState(() {
    _isTyping = true;
  });

  _scrollToBottom();


  await Future<void>.delayed(
    const Duration(seconds: 2),
  );

  if (!mounted) {
    return;
  }

  setState(() {
    _isTyping = false;

      // Temporary response until the backend is connected.
    _messages.add(
      ChatMessage(
        text:
            "I'm not connected to the SOP database yet.\n\n"
            'This is where the AI response will appear.',
        isUser: false,
      ),
    );
  });

  _scrollToBottom();
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (!_scrollController.hasClients) {
        return;
      }

      _scrollController.animateTo(
        _scrollController.position.maxScrollExtent,
        duration: const Duration(milliseconds: 300),
        curve: Curves.easeOut,
      );
    });
  }

  @override
  void dispose() {
    _controller.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('YWCC SOP Assistant'),
      ),
      body: Column(
        children: [
          Expanded(
            child: ListView.builder(
              controller: _scrollController,
              padding: const EdgeInsets.all(16),
              itemCount: _messages.length + (_isTyping ? 1 : 0),
              itemBuilder: (context, index) {
                  if (_isTyping && index == _messages.length) {
                    return const TypingIndicator();
                  }
                  
                return ChatBubble(
                  message: _messages[index],
                );
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
                    enabled: !_isTyping,
                    textInputAction: TextInputAction.send,
                    onSubmitted: (_) => _sendMessage(),
                    decoration: InputDecoration(
                      hintText: 'Ask an SOP question...',
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                  ),
                ),
                const SizedBox(width: 10),
                FilledButton.icon(
                  onPressed: _isTyping ? null : _sendMessage,
                  icon: const Icon(Icons.send),
                  label: const Text('Send'),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}