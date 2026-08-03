import 'dart:convert';
import 'package:http/http.dart' as http;

class ChatResponse {
  final String text;
  final String? source;

  const ChatResponse({
    required this.text,
    this.source,
  });
}

class ChatService {
  static final Uri _chatUrl = Uri.parse(
    'http://127.0.0.1:8000/chat',
  );

  Future<ChatResponse> getResponse(String question) async {
    final http.Response response = await http
        .post(
          _chatUrl,
          headers: {
            'Content-Type': 'application/json',
          },
          body: jsonEncode({
            'question': question,
          }),
        )
        .timeout(
          const Duration(seconds: 15),
        );

    if (response.statusCode != 200) {
      throw Exception(
        'Backend request failed with status '
        '${response.statusCode}.',
      );
    }

    final dynamic decodedBody = jsonDecode(response.body);

    if (decodedBody is! Map<String, dynamic>) {
      throw const FormatException(
        'The backend returned an invalid response.',
      );
    }

    final dynamic answer = decodedBody['answer'];
    final dynamic source = decodedBody['source'];

    if (answer is! String || answer.trim().isEmpty) {
      throw const FormatException(
        'The backend response did not contain an answer.',
      );
    }

    return ChatResponse(
      text: answer,
      source: source is String && source.trim().isNotEmpty
          ? source
          : null,
    );
  }
}