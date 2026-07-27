import 'package:flutter/material.dart';

class DashboardScreen extends StatelessWidget {
  const DashboardScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text(
          "YWCC SOP Assistant",
        ),
      ),

      body: Padding(
        padding: const EdgeInsets.all(24),

        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,

          children: [

            const Text(
              "Welcome Back",
              style: TextStyle(
                fontSize: 28,
                fontWeight: FontWeight.bold,
              ),
            ),

            const SizedBox(height: 20),

            Card(
              child: ListTile(
                leading: const Icon(Icons.chat),
                title: const Text(
                  "Ask an SOP Question",
                ),
                subtitle: const Text(
                  "Get step-by-step procedures",
                ),
                trailing: const Icon(
                  Icons.arrow_forward,
                ),
              ),
            ),

            const SizedBox(height: 15),

            Card(
              child: ListTile(
                leading: const Icon(Icons.folder),
                title: const Text(
                  "SOP Library",
                ),
                subtitle: const Text(
                  "Browse approved procedures",
                ),
                trailing: const Icon(
                  Icons.arrow_forward,
                ),
              ),
            ),

            const SizedBox(height: 15),

            Card(
              child: ListTile(
                leading: const Icon(Icons.history),
                title: const Text(
                  "Recent Activity",
                ),
                subtitle: const Text(
                  "View previous searches",
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}