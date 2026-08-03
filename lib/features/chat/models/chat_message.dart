class ChatMessage {
  final String text;
  final bool isUser;
  final String? source;
  final DateTime timestamp;

  ChatMessage({
    required this.text,
    required this.isUser,
    this.source,
    DateTime? timestamp,
  }) : timestamp = timestamp ?? DateTime.now();
  }