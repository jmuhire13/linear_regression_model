import 'package:flutter/material.dart';
import 'prediction_page.dart';

void main() {
  runApp(const MathScorePredictorApp());
}

class MathScorePredictorApp extends StatelessWidget {
  const MathScorePredictorApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Math Score Predictor',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorSchemeSeed: Colors.indigo,
        useMaterial3: true,
        brightness: Brightness.light,
      ),
      home: const PredictionPage(),
    );
  }
}