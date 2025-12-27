#!/usr/bin/env node

/**
 * Railway Environment Variables Checker
 * Verifies that all required environment variables for Saleor are set
 */

const requiredVars = {
  'SECRET_KEY': {
    required: true,
    description: 'Django secret key for cryptographic signing',
    generate: 'openssl rand -hex 32'
  },
  'DATABASE_URL': {
    required: true,
    description: 'PostgreSQL connection string (auto-set by Railway PostgreSQL service)',
    autoSet: true
  },
  'ALLOWED_HOSTS': {
    required: true,
    description: 'Comma-separated list of allowed hosts (e.g., *.railway.app,your-app.railway.app)',
    example: '*.railway.app,your-app-name.railway.app'
  }
};

const optionalVars = {
  'DEBUG': {
    recommended: false,
    description: 'Debug mode (should be False for production)',
    defaultValue: 'False'
  },
  'CELERY_BROKER_URL': {
    recommended: true,
    description: 'Celery broker URL (should reference Redis service)',
    example: '${{Redis.REDIS_URL}}'
  },
  'CELERY_RESULT_BACKEND': {
    recommended: true,
    description: 'Celery result backend (should reference Redis service)',
    example: '${{Redis.REDIS_URL}}'
  },
  'REDIS_URL': {
    recommended: true,
    description: 'Redis connection string (auto-set by Railway Redis service)',
    autoSet: true
  },
  'STATIC_URL': {
    recommended: false,
    description: 'Static files URL',
    defaultValue: '/static/'
  },
  'MEDIA_URL': {
    recommended: false,
    description: 'Media files URL',
    defaultValue: '/media/'
  },
  'SITE_NAME': {
    recommended: false,
    description: 'Site name',
    defaultValue: 'Saleor Store'
  },
  'SECURE_SSL_REDIRECT': {
    recommended: true,
    description: 'Redirect HTTP to HTTPS',
    defaultValue: 'True'
  },
  'SESSION_COOKIE_SECURE': {
    recommended: true,
    description: 'Use secure cookies',
    defaultValue: 'True'
  },
  'CSRF_COOKIE_SECURE': {
    recommended: true,
    description: 'Use secure CSRF cookies',
    defaultValue: 'True'
  }
};

function checkVariables() {
  console.log('🔍 Checking Railway Environment Variables for Saleor\n');
  console.log('='.repeat(60));
  console.log('');

  let hasErrors = false;
  let hasWarnings = false;

  // Check required variables
  console.log('📋 REQUIRED VARIABLES:\n');
  for (const [varName, config] of Object.entries(requiredVars)) {
    const value = process.env[varName];
    const isSet = value !== undefined && value !== '';
    
    if (!isSet && config.required) {
      console.log(`❌ ${varName}: NOT SET`);
      console.log(`   Description: ${config.description}`);
      if (config.generate) {
        console.log(`   Generate: ${config.generate}`);
      }
      if (config.autoSet) {
        console.log(`   ⚠️  This should be auto-set by Railway service`);
      }
      if (config.example) {
        console.log(`   Example: ${config.example}`);
      }
      console.log('');
      hasErrors = true;
    } else if (isSet) {
      // Mask sensitive values
      let displayValue = value;
      if (varName === 'SECRET_KEY' || varName === 'DATABASE_URL') {
        displayValue = value.substring(0, 20) + '...' + value.substring(value.length - 10);
      }
      console.log(`✅ ${varName}: SET`);
      console.log(`   Value: ${displayValue}`);
      console.log('');
    } else {
      console.log(`⚠️  ${varName}: NOT SET (but marked as required)`);
      console.log('');
      hasWarnings = true;
    }
  }

  // Check optional/recommended variables
  console.log('\n📋 OPTIONAL/RECOMMENDED VARIABLES:\n');
  for (const [varName, config] of Object.entries(optionalVars)) {
    const value = process.env[varName];
    const isSet = value !== undefined && value !== '';
    
    if (!isSet) {
      if (config.recommended) {
        console.log(`⚠️  ${varName}: NOT SET (recommended)`);
        console.log(`   Description: ${config.description}`);
        if (config.example) {
          console.log(`   Example: ${config.example}`);
        }
        console.log('');
        hasWarnings = true;
      } else {
        console.log(`⚪ ${varName}: NOT SET (optional)`);
        if (config.defaultValue) {
          console.log(`   Default: ${config.defaultValue}`);
        }
        console.log('');
      }
    } else {
      let displayValue = value;
      if (varName.includes('URL') || varName === 'SECRET') {
        displayValue = value.substring(0, 30) + '...';
      }
      console.log(`✅ ${varName}: SET`);
      console.log(`   Value: ${displayValue}`);
      console.log('');
    }
  }

  // Summary
  console.log('\n' + '='.repeat(60));
  console.log('\n📊 SUMMARY:\n');

  if (hasErrors) {
    console.log('❌ ERRORS FOUND: Some required variables are missing!');
    console.log('   Fix these before deploying.\n');
  } else {
    console.log('✅ All required variables are set!\n');
  }

  if (hasWarnings) {
    console.log('⚠️  WARNINGS: Some recommended variables are missing.');
    console.log('   Consider setting these for optimal configuration.\n');
  }

  // Generate Railway CLI commands
  console.log('💡 To set variables in Railway using CLI:\n');
  console.log('   railway variables set SECRET_KEY=$(openssl rand -hex 32)');
  console.log('   railway variables set ALLOWED_HOSTS="*.railway.app,your-app-name.railway.app"');
  console.log('   railway variables set DEBUG=False');
  console.log('   railway variables set CELERY_BROKER_URL=\\${{Redis.REDIS_URL}}');
  console.log('   railway variables set CELERY_RESULT_BACKEND=\\${{Redis.REDIS_URL}}');
  console.log('');

  // Exit with error code if there are errors
  process.exit(hasErrors ? 1 : 0);
}

// Run the check
checkVariables();

