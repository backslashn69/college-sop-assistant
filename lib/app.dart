import 'package:flutter/material.dart';
import 'features/auth/screens/login_screen.dart';

class SOPAssistantApp extends StatelessWidget {
  const SOPAssistantApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'YWCC SOP Assistant',
      debugShowCheckedModeBanner: false,

      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: Colors.indigo,
        ),
        useMaterial3: true,
      ),

      home: const LoginScreen(),
    );
  }
}