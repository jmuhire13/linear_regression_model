import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

class PredictionPage extends StatefulWidget {
  const PredictionPage({super.key});

  @override
  State<PredictionPage> createState() => _PredictionPageState();
}

class _PredictionPageState extends State<PredictionPage> {
  static const String apiBaseUrl =
      'https://math-score-predictor-d8z2.onrender.com';

  final TextEditingController _readingScoreController = TextEditingController();
  final TextEditingController _writingScoreController = TextEditingController();

  String _selectedGender = 'female';
  String _selectedLunch = 'standard';
  String _selectedTestPrep = 'none';
  String _selectedParentalEdu = "bachelor's degree";

  final List<String> _genderOptions = ['female', 'male'];
  final List<String> _lunchOptions = ['standard', 'free/reduced'];
  final List<String> _testPrepOptions = ['none', 'completed'];
  final List<String> _parentalEduOptions = [
    'some high school',
    'high school',
    'some college',
    "associate's degree",
    "bachelor's degree",
    "master's degree",
  ];

  String? _predictionResult;
  String? _modelUsed;
  bool _isLoading = false;
  String? _errorMessage;

  Future<void> _predict() async {
    final readingText = _readingScoreController.text.trim();
    final writingText = _writingScoreController.text.trim();

    if (readingText.isEmpty || writingText.isEmpty) {
      setState(() {
        _errorMessage = 'Please enter both reading and writing scores.';
        _predictionResult = null;
      });
      return;
    }

    final readingScore = int.tryParse(readingText);
    final writingScore = int.tryParse(writingText);

    if (readingScore == null ||
        writingScore == null ||
        readingScore < 0 ||
        readingScore > 100 ||
        writingScore < 0 ||
        writingScore > 100) {
      setState(() {
        _errorMessage = 'Scores must be whole numbers between 0 and 100.';
        _predictionResult = null;
      });
      return;
    }

    setState(() {
      _isLoading = true;
      _errorMessage = null;
      _predictionResult = null;
    });

    try {
      final response = await http.post(
        Uri.parse('$apiBaseUrl/predict'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'gender': _selectedGender,
          'parental_level_of_education': _selectedParentalEdu,
          'lunch': _selectedLunch,
          'test_preparation_course': _selectedTestPrep,
          'reading_score': readingScore,
          'writing_score': writingScore,
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        setState(() {
          _predictionResult = data['predicted_math_score'].toStringAsFixed(2);
          _modelUsed = data['model_used'];
        });
      } else {
        final data = jsonDecode(response.body);
        setState(() {
          _errorMessage = data['detail'] ?? 'Prediction failed.';
        });
      }
    } catch (e) {
      setState(() {
        _errorMessage = 'Connection error: $e';
      });
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  Widget _buildDropdown({
    required String label,
    required String value,
    required List<String> items,
    required ValueChanged<String?> onChanged,
    required IconData icon,
  }) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 16),
      child: DropdownButtonFormField<String>(
        value: value,
        decoration: InputDecoration(
          labelText: label,
          prefixIcon: Icon(icon),
          border: const OutlineInputBorder(),
        ),
        items: items
            .map((e) => DropdownMenuItem(value: e, child: Text(e)))
            .toList(),
        onChanged: onChanged,
      ),
    );
  }

  Widget _buildScoreField({
    required String label,
    required TextEditingController controller,
    required IconData icon,
  }) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 16),
      child: TextField(
        controller: controller,
        keyboardType: TextInputType.number,
        decoration: InputDecoration(
          labelText: label,
          hintText: '0 – 100',
          prefixIcon: Icon(icon),
          border: const OutlineInputBorder(),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Math Score Predictor'),
        centerTitle: true,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Card(
              color: theme.colorScheme.primaryContainer,
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  children: [
                    Icon(Icons.school,
                        size: 40, color: theme.colorScheme.primary),
                    const SizedBox(height: 8),
                    Text(
                      'Predict Student Math Score',
                      style: theme.textTheme.titleLarge?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'Enter student details below to get a prediction.',
                      style: theme.textTheme.bodyMedium,
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 24),
            _buildDropdown(
              label: 'Gender',
              value: _selectedGender,
              items: _genderOptions,
              onChanged: (v) => setState(() => _selectedGender = v!),
              icon: Icons.person,
            ),
            _buildDropdown(
              label: 'Parental Level of Education',
              value: _selectedParentalEdu,
              items: _parentalEduOptions,
              onChanged: (v) => setState(() => _selectedParentalEdu = v!),
              icon: Icons.family_restroom,
            ),
            _buildDropdown(
              label: 'Lunch Type',
              value: _selectedLunch,
              items: _lunchOptions,
              onChanged: (v) => setState(() => _selectedLunch = v!),
              icon: Icons.restaurant,
            ),
            _buildDropdown(
              label: 'Test Preparation Course',
              value: _selectedTestPrep,
              items: _testPrepOptions,
              onChanged: (v) => setState(() => _selectedTestPrep = v!),
              icon: Icons.menu_book,
            ),
            _buildScoreField(
              label: 'Reading Score',
              controller: _readingScoreController,
              icon: Icons.auto_stories,
            ),
            _buildScoreField(
              label: 'Writing Score',
              controller: _writingScoreController,
              icon: Icons.edit_note,
            ),
            const SizedBox(height: 8),
            SizedBox(
              height: 52,
              child: FilledButton.icon(
                onPressed: _isLoading ? null : _predict,
                icon: _isLoading
                    ? const SizedBox(
                        width: 20,
                        height: 20,
                        child: CircularProgressIndicator(
                          strokeWidth: 2,
                          color: Colors.white,
                        ),
                      )
                    : const Icon(Icons.calculate),
                label: Text(
                  _isLoading ? 'Predicting...' : 'Predict',
                  style: const TextStyle(fontSize: 16),
                ),
              ),
            ),
            const SizedBox(height: 24),
            if (_errorMessage != null)
              Card(
                color: theme.colorScheme.errorContainer,
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Row(
                    children: [
                      Icon(Icons.error_outline, color: theme.colorScheme.error),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Text(
                          _errorMessage!,
                          style: TextStyle(color: theme.colorScheme.error),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            if (_predictionResult != null)
              Card(
                color: theme.colorScheme.secondaryContainer,
                child: Padding(
                  padding: const EdgeInsets.all(20),
                  child: Column(
                    children: [
                      Icon(Icons.check_circle,
                          size: 48, color: theme.colorScheme.secondary),
                      const SizedBox(height: 12),
                      Text(
                        'Predicted Math Score',
                        style: theme.textTheme.titleMedium,
                      ),
                      const SizedBox(height: 8),
                      Text(
                        _predictionResult!,
                        style: theme.textTheme.displaySmall?.copyWith(
                          fontWeight: FontWeight.bold,
                          color: theme.colorScheme.secondary,
                        ),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        'Model: ${_modelUsed ?? "N/A"}',
                        style: theme.textTheme.bodySmall,
                      ),
                    ],
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }

  @override
  void dispose() {
    _readingScoreController.dispose();
    _writingScoreController.dispose();
    super.dispose();
  }
}
