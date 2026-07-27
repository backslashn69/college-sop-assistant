class ChatMessage {
  final String text;
  final bool isUser;
  final String? source;

  ChatMessage({
    required this.text,
    required this.isUser,
    this.source,
  });
}