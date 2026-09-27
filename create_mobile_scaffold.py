"""
Creates a mobile_app scaffold (React Native / Expo) in this repository.
Run: python create_mobile_scaffold.py

This script will create:
- mobile_app/package.json
- mobile_app/App.js
- mobile_app/services/api.js
- mobile_app/screens/LoginScreen.js
- mobile_app/screens/DashboardScreen.js

After running:
1. cd mobile_app
2. npm install
3. npx expo start

Adjust BASE_URL in services/api.js to point to your backend (use 10.0.2.2 for Android emulator).
"""
import os

files = {
    "mobile_app/package.json": '''{
  "name": "mengo-hub-mobile",
  "version": "0.0.1",
  "private": true,
  "main": "node_modules/expo/AppEntry.js",
  "scripts": {
    "start": "expo start",
    "android": "expo run:android",
    "ios": "expo run:ios"
  },
  "dependencies": {
    "expo": "~48.0.0",
    "react": "18.2.0",
    "react-native": "0.71.8",
    "axios": "^1.4.0"
  }
}
''',
    "mobile_app/App.js": '''import React, { useState } from 'react';
import { View } from 'react-native';
import LoginScreen from './screens/LoginScreen';
import DashboardScreen from './screens/DashboardScreen';

export default function App() {
  const [screen, setScreen] = useState('Login');
  const [userId, setUserId] = useState(null);

  return (
    <View style={{flex:1}}>
      {screen === 'Login' && (
        <LoginScreen onLogin={(id) => { setUserId(id); setScreen('Dashboard'); }} />
      )}
      {screen === 'Dashboard' && (
        <DashboardScreen userId={userId} />
      )}
    </View>
  );
}
''',
    "mobile_app/services/api.js": '''import axios from 'axios';

// Default base URL for Android emulator. Adjust as needed for device/emulator.
const BASE_URL = 'http://10.0.2.2:5000';

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' }
});

export default api;
''',
    "mobile_app/screens/LoginScreen.js": '''import React, { useState } from 'react';
import { View, Text, TextInput, Button, StyleSheet } from 'react-native';
import api from '../services/api';

export default function LoginScreen({ onLogin }) {
  const [userId, setUserId] = useState('student1');
  const [deviceToken, setDeviceToken] = useState('device-token-123');

  const registerDevice = async () => {
    try {
      const res = await api.post('/api/mobile/register_device', { user_id: userId, device_token: deviceToken, platform: 'android' });
      if (res.data && res.data.success) {
        alert('Device registered');
        onLogin(userId);
      } else {
        alert('Register failed: ' + JSON.stringify(res.data));
      }
    } catch (e) {
      alert('Error: ' + e.message);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Mengo-Hub Mobile Test</Text>
      <TextInput style={styles.input} value={userId} onChangeText={setUserId} placeholder="User ID" />
      <TextInput style={styles.input} value={deviceToken} onChangeText={setDeviceToken} placeholder="Device Token" />
      <Button title="Register Device & Go" onPress={registerDevice} />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 20, justifyContent: 'center' },
  title: { fontSize: 20, marginBottom: 20, textAlign: 'center' },
  input: { borderWidth: 1, padding: 10, marginBottom: 12, borderRadius: 6 }
});
''',
    "mobile_app/screens/DashboardScreen.js": '''import React, { useEffect, useState } from 'react';
import { View, Text, Button, FlatList, StyleSheet } from 'react-native';
import api from '../services/api';

export default function DashboardScreen({ userId }) {
  const [dashboard, setDashboard] = useState(null);

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const res = await api.get('/api/dashboard/student');
        if (res.data && res.data.success) setDashboard(res.data.dashboard);
        else alert('Failed to load dashboard');
      } catch (e) {
        alert('Error: ' + e.message);
      }
    };
    fetchDashboard();
  }, []);

  if (!dashboard) return (
    <View style={styles.container}><Text>Loading...</Text></View>
  );

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Student Dashboard</Text>
      <Text>Total Exams: {dashboard.statistics.total_exams}</Text>
      <Text>Avg %: {dashboard.statistics.avg_percentage}</Text>
      <Text>Total Points: {dashboard.statistics.total_points}</Text>
      <Text style={{marginTop:10, fontWeight:'bold'}}>Recent Exams:</Text>
      <FlatList
        data={dashboard.recent_exams}
        keyExtractor={(item) => item.exam_id.toString()}
        renderItem={({item}) => (
          <View style={{padding:8}}>
            <Text>{item.exam_name} - {item.score}/{item.max_score}</Text>
          </View>
        )}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 20 },
  title: { fontSize: 20, marginBottom: 12 }
});
'''
}

if __name__ == '__main__':
    cwd = os.getcwd()
    for rel_path, content in files.items():
        full_path = os.path.join(cwd, rel_path.replace('/', os.sep))
        dir_path = os.path.dirname(full_path)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'Wrote {full_path}')
    print('\nScaffold created. Run:\n  cd mobile_app\n  npm install\n  npx expo start\n')
