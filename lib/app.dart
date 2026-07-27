import 'package:flutter/material.dart';
import 'package:college_sop_assistant/features/auth/screens/login_screen.dart';
import 'package:college_sop_assistant/core/theme/app_theme.dart';

class SOPAssistantApp extends StatelessWidget {
  const SOPAssistantApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'YWCC SOP Assistant',
      debugShowCheckedModeBanner: false,

      theme: AppTheme.lightTheme,

      home: const LoginScreen(),
    );
  }
}