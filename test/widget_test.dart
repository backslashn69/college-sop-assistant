import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:college_sop_assistant/app.dart';

void main() {
  testWidgets('SOP Assistant launches successfully', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(const SOPAssistantApp());
    await tester.pumpAndSettle();

    expect(find.byType(MaterialApp), findsOneWidget);
    expect(find.byType(Scaffold), findsOneWidget);
  });
}