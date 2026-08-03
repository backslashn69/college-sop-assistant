class ChatService {
  Future<String> getResponse(String question) async {

    await Future<void>.delayed(
      const Duration(seconds: 2),
    );

    return "I'm not connected to the SOP database yet.\n\n"
        "This is where the AI response for \"$question\" will appear.";
  }
}