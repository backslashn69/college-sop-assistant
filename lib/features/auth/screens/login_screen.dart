import 'package:flutter/material.dart';
import '../../../core/navigation/app_navigation.dart';


class LoginScreen extends StatelessWidget {
  const LoginScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: SizedBox(
          width: 400,
          child: Padding(
            padding: const EdgeInsets.all(24),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Icon(
                  Icons.description,
                  size: 80,
                  color: Colors.indigo,
                ),

                const SizedBox(height: 20),

                const Text(
                  "YWCC SOP Assistant",
                  style: TextStyle(
                    fontSize: 32,
                    fontWeight: FontWeight.bold,
                  ),
                ),

                const SizedBox(height: 8),

                const Text(
                  "Sign in to continue",
                ),

                const SizedBox(height: 40),

                TextField(
                  decoration: InputDecoration(
                    labelText: "Email",
                    border: OutlineInputBorder(),
                  ),
                ),

                const SizedBox(height: 20),

                TextField(
                  obscureText: true,
                  decoration: InputDecoration(
                    labelText: "Password",
                    border: OutlineInputBorder(),
                  ),
                ),

                const SizedBox(height: 30),

                SizedBox(
                  width: double.infinity,
                  child: FilledButton(
                    onPressed: () {  
                        Navigator.push(
                            context,
                            MaterialPageRoute(
                                builder: (context) =>
                                    const AppNavigation(),
                            ),
                        );                            
                    },
                    child: const Text("Sign In"),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}