import 'package:flutter/material.dart';
import 'package:college_sop_assistant/features/auth/screens/dashboard_screen.dart';


class AppNavigation extends StatefulWidget {
  const AppNavigation({super.key});

  @override
  State<AppNavigation> createState() => _AppNavigationState();
}


class _AppNavigationState extends State<AppNavigation> {

  int selectedIndex = 0;


  final List<Widget> pages = [

    const DashboardScreen(),

    const Center(
      child: Text(
        "SOP Chat Coming Soon",
        style: TextStyle(fontSize: 24),
      ),
    ),

    const Center(
      child: Text(
        "SOP Library Coming Soon",
        style: TextStyle(fontSize: 24),
      ),
    ),

    const Center(
      child: Text(
        "Bookmarks Coming Soon",
        style: TextStyle(fontSize: 24),
      ),
    ),

    const Center(
      child: Text(
        "Settings Coming Soon",
        style: TextStyle(fontSize: 24),
      ),
    ),

  ];


  @override
  Widget build(BuildContext context) {

    return Scaffold(

      body: Row(

        children: [

          NavigationRail(

            selectedIndex: selectedIndex,

            onDestinationSelected: (index){

              setState(() {

                selectedIndex = index;

              });

            },


            labelType: NavigationRailLabelType.all,


            destinations: const [

              NavigationRailDestination(
                icon: Icon(Icons.dashboard),
                label: Text("Dashboard"),
              ),


              NavigationRailDestination(
                icon: Icon(Icons.chat),
                label: Text("Chat"),
              ),


              NavigationRailDestination(
                icon: Icon(Icons.folder),
                label: Text("SOP Library"),
              ),


              NavigationRailDestination(
                icon: Icon(Icons.bookmark),
                label: Text("Bookmarks"),
              ),


              NavigationRailDestination(
                icon: Icon(Icons.settings),
                label: Text("Settings"),
              ),

            ],

          ),


          Expanded(
            child: pages[selectedIndex],
          ),

        ],

      ),

    );

  }

}