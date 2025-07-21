#!/usr/bin/env node

// Simple test script to verify MyBella AI server functionality
const axios = require('axios');

const API_BASE = 'http://localhost:3001/api';

async function testServer() {
  console.log('🧪 Testing MyBella AI Server...\n');
  
  try {
    // Test 1: Health check
    console.log('1. Testing health endpoint...');
    const healthResponse = await axios.get(`${API_BASE}/health`);
    console.log('✅ Health check passed:', healthResponse.data.message);
    
    // Test 2: Chat endpoint (basic functionality)
    console.log('\n2. Testing chat endpoint...');
    const chatResponse = await axios.post(`${API_BASE}/chat`, {
      message: 'Hello Bella, this is a test message.',
      userId: 'test-user'
    });
    console.log('✅ Chat test passed');
    console.log('🤖 Bella responded:', chatResponse.data.response.substring(0, 100) + '...');
    
    console.log('\n🎉 All tests passed! MyBella AI is ready to use.');
    console.log('🌐 Frontend: http://localhost:3000');
    console.log('🔧 Backend: http://localhost:3001');
    
  } catch (error) {
    console.error('❌ Test failed:', error.message);
    if (error.response) {
      console.error('Response status:', error.response.status);
      console.error('Response data:', error.response.data);
    }
    
    if (error.code === 'ECONNREFUSED') {
      console.log('\n💡 Make sure the server is running with: npm run dev');
    }
  }
}

// Run the test
testServer();