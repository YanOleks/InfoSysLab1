import React from 'react';
import { Form, Input, Button, message, Card } from 'antd';
import api from '../api';

export default function LoginPage({ onLogin }) {
  const [form] = Form.useForm();

  const handleLogin = async () => {
    try {
      const values = await form.validateFields();
      const res = await api.post('/auth/login', values);
      onLogin(res.data.access_token);
      message.success('Logged in successfully');
    } catch (err) {
      if (err.response?.status === 401) {
        message.error('Incorrect username or password');
      } else if (err.errorFields) {
        // Validation error
      } else {
        message.error('Login failed');
      }
    }
  };

  const handleRegister = async () => {
    try {
      const values = await form.validateFields();
      await api.post('/auth/register', values);
      message.success('Registered successfully! You can now login.');
    } catch (err) {
      if (err.response?.status === 400) {
        message.error('Username already registered');
      } else if (err.errorFields) {
        // Validation error
      } else {
        message.error('Registration failed');
      }
    }
  };

  return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', background: '#f0f2f5' }}>
      <Card title="Lightweight Drive" style={{ width: 400 }}>
        <Form form={form} layout="vertical">
          <Form.Item name="username" label="Username" rules={[{ required: true, message: 'Please input your username!' }]}>
            <Input />
          </Form.Item>
          <Form.Item name="password" label="Password" rules={[{ required: true, message: 'Please input your password!' }]}>
            <Input.Password />
          </Form.Item>
          <Form.Item>
            <Button type="primary" onClick={handleLogin} style={{ width: '100%', marginBottom: 10 }}>Login</Button>
            <Button onClick={handleRegister} style={{ width: '100%' }}>Register</Button>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
}
