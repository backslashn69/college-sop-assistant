class ChatResponse {
  final String text;
  final String? source;

  const ChatResponse({
    required this.text,
    this.source,
  });
}

class ChatService {
  Future<ChatResponse> getResponse(String question) async {
    // Simulates waiting for the future backend response.
    await Future<void>.delayed(
      const Duration(seconds: 2),
    );

    return ChatResponse(
      text:
          "I'm not connected to the SOP database yet.\n\n"
          "This is where the AI response for \"$question\" will appear.",
      source: 'Registrar SOP v3.2 • Section 4.1 • Page 18',
    );
  }
}