import 'package:flutter/material.dart';
import 'package:college_sop_assistant/features/chat/models/chat_message.dart';

class ChatBubble extends StatelessWidget {
  final ChatMessage message;

  const ChatBubble({
    super.key,
    required this.message,
  });

  @override
  Widget build(BuildContext context) {
    final isUser = message.isUser;

    return Align(
      alignment:
          isUser ? Alignment.centerRight : Alignment.centerLeft,
      child: ConstrainedBox(
        constraints: const BoxConstraints(
          maxWidth: 650,
        ),
        child: Container(
          margin: const EdgeInsets.symmetric(vertical: 8),
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: isUser
                ? Theme.of(context).colorScheme.primary
                : Colors.white,
            borderRadius: BorderRadius.only(
              topLeft: const Radius.circular(18),
              topRight: const Radius.circular(18),
              bottomLeft: Radius.circular(isUser ? 18 : 4),
              bottomRight: Radius.circular(isUser ? 4 : 18),
            ),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withOpacity(.08),
                blurRadius: 10,
                offset: const Offset(0, 4),
              ),
            ],
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [

              Text(
                message.text,
                style: TextStyle(
                  fontSize: 16,
                  height: 1.5,
                  color: isUser
                      ? Colors.white
                      : Colors.black87,
                ),
              ),

              if (message.source != null) ...[
                const SizedBox(height: 14),
                Divider(
                  color: Colors.grey.shade300,
                ),
                const SizedBox(height: 6),

                Row(
                  children: [
                    Icon(
                      Icons.description_outlined,
                      size: 18,
                      color: Colors.blueGrey.shade700,
                    ),
                    const SizedBox(width: 6),

                    Expanded(
                      child: Text(
                        message.source!,
                        style: TextStyle(
                          fontSize: 13,
                          color: Colors.blueGrey.shade700,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ),
                  ],
                ),
              ]
            ],
          ),
        ),
      ),
    );
  }
}