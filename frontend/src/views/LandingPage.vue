<template>
  <div>
    <!-- Hero -->
    <section class="max-w-5xl mx-auto px-4 pt-24 pb-16 text-center">
      <div class="inline-flex items-center gap-1.5 px-3 py-1 mb-6 rounded-full bg-brand-50 border border-brand-200 text-brand-700 text-xs font-medium">
        <span class="w-1.5 h-1.5 rounded-full bg-brand-500 animate-pulse"></span>
        AI-Powered
      </div>
      <h1 class="text-4xl md:text-6xl font-extrabold tracking-tight mb-6 text-gray-900">
        Never write a<br />
        <span class="gradient-text">changelog</span> by hand again
      </h1>
      <p class="text-lg text-gray-500 max-w-2xl mx-auto mb-10">
        LogFast reads your Git commits, uses AI to understand what changed,
        and generates customer-ready changelogs — in seconds.
      </p>
      <div class="flex items-center justify-center gap-3">
        <a :href="API_BASE + '/api/auth/login'" class="bg-gray-900 hover:bg-gray-800 text-white px-6 py-3 rounded-xl text-sm font-semibold transition flex items-center gap-2 shadow-sm">
          <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/></svg>
          Connect with GitHub
        </a>
        <a href="#how-it-works" class="text-sm text-gray-500 hover:text-gray-900 transition">See how it works →</a>
      </div>
    </section>

    <!-- How it works -->
    <section id="how-it-works" class="max-w-4xl mx-auto px-4 py-20">
      <h2 class="text-2xl md:text-3xl font-bold text-center mb-14 text-gray-900">Three steps to a beautiful changelog</h2>
      <div class="grid md:grid-cols-3 gap-8">
        <div class="text-center">
          <div class="w-14 h-14 bg-brand-50 rounded-xl flex items-center justify-center mx-auto mb-4 text-2xl">🔗</div>
          <h3 class="font-semibold text-gray-900 mb-2">1. Connect your repo</h3>
          <p class="text-sm text-gray-500">Grant LogFast access to your GitHub repository. Takes 30 seconds.</p>
        </div>
        <div class="text-center">
          <div class="w-14 h-14 bg-brand-50 rounded-xl flex items-center justify-center mx-auto mb-4 text-2xl">🤖</div>
          <h3 class="font-semibold text-gray-900 mb-2">2. AI reads your commits</h3>
          <p class="text-sm text-gray-500">Our AI analyzes commit diffs and messages to understand what actually changed for users.</p>
        </div>
        <div class="text-center">
          <div class="w-14 h-14 bg-brand-50 rounded-xl flex items-center justify-center mx-auto mb-4 text-2xl">🚀</div>
          <h3 class="font-semibold text-gray-900 mb-2">3. Publish & delight users</h3>
          <p class="text-sm text-gray-500">One click publish. Your changelog gets a beautiful page at <code class="text-brand-600 bg-brand-50 px-1 rounded">logfast.app/p/you/repo</code>.</p>
        </div>
      </div>
    </section>

    <!-- Example changelog -->
    <section class="max-w-3xl mx-auto px-4 py-12 mb-20">
      <div class="bg-white border border-gray-200 rounded-2xl overflow-hidden shadow-sm">
        <div class="bg-gray-50 px-6 py-3 border-b border-gray-200 flex items-center gap-2 text-sm text-gray-400">
          <span class="w-3 h-3 rounded-full bg-red-400"></span>
          <span class="w-3 h-3 rounded-full bg-yellow-400"></span>
          <span class="w-3 h-3 rounded-full bg-green-400"></span>
          <span class="ml-4 text-gray-500">logfast.app/p/acme/saas-dashboard</span>
        </div>
        <div class="p-8">
          <p class="text-xs text-gray-400 mb-1">v2.4.0 · 2 hours ago</p>
          <h3 class="text-xl font-bold text-gray-900 mb-6">Faster Exports & Dark Mode</h3>
          <div class="space-y-5">
            <div>
              <p class="text-sm font-semibold text-brand-600 mb-2">🚀 New Features</p>
              <ul class="space-y-1.5 text-sm text-gray-600">
                <li class="flex gap-2"><span class="text-brand-500">•</span> You can now switch between light and dark mode from the settings panel.</li>
                <li class="flex gap-2"><span class="text-brand-500">•</span> CSV exports now support custom date ranges and column selection.</li>
              </ul>
            </div>
            <div>
              <p class="text-sm font-semibold text-blue-600 mb-2">✨ Improvements</p>
              <ul class="space-y-1.5 text-sm text-gray-600">
                <li class="flex gap-2"><span class="text-blue-500">•</span> Dashboard loads 3x faster — we optimized the data fetching pipeline.</li>
                <li class="flex gap-2"><span class="text-blue-500">•</span> Search now includes results from archived projects.</li>
              </ul>
            </div>
            <div>
              <p class="text-sm font-semibold text-orange-600 mb-2">🐛 Bug Fixes</p>
              <ul class="space-y-1.5 text-sm text-gray-600">
                <li class="flex gap-2"><span class="text-orange-500">•</span> Fixed an issue where notification emails were sent twice for team invites.</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Pricing -->
    <section class="max-w-4xl mx-auto px-4 py-20" id="pricing">
      <h2 class="text-2xl md:text-3xl font-bold text-center mb-4 text-gray-900">Simple pricing</h2>
      <p class="text-center text-gray-500 mb-12">Start free, upgrade when you need more.</p>
      <div class="grid md:grid-cols-3 gap-6">
        <div class="bg-white border border-gray-200 rounded-xl p-6 flex flex-col shadow-sm">
          <h3 class="font-semibold text-lg text-gray-900 mb-1">Free</h3>
          <p class="text-sm text-gray-500 mb-4">For open source projects</p>
          <p class="text-3xl font-bold text-gray-900 mb-6">$0<span class="text-base font-normal text-gray-400">/mo</span></p>
          <ul class="space-y-2 text-sm text-gray-600 flex-1">
            <li class="flex gap-2"><span class="text-brand-500">✓</span> 1 public repo</li>
            <li class="flex gap-2"><span class="text-brand-500">✓</span> AI-generated changelogs</li>
            <li class="flex gap-2"><span class="text-brand-500">✓</span> Public changelog page</li>
            <li class="flex gap-2"><span class="text-brand-500">✓</span> Basic customization</li>
          </ul>
          <a :href="API_BASE + '/api/auth/login'" class="mt-6 block text-center border border-gray-300 text-gray-700 py-2.5 rounded-lg text-sm hover:border-gray-400 transition">Get Started</a>
        </div>
        <div class="bg-white border-2 border-brand-500 rounded-xl p-6 flex flex-col relative shadow-sm">
          <span class="absolute -top-3 left-1/2 -translate-x-1/2 bg-brand-500 text-white text-xs font-bold px-3 py-0.5 rounded-full">POPULAR</span>
          <h3 class="font-semibold text-lg text-gray-900 mb-1">Starter</h3>
          <p class="text-sm text-gray-500 mb-4">For indie makers</p>
          <p class="text-3xl font-bold text-gray-900 mb-6">$9<span class="text-base font-normal text-gray-400">/mo</span></p>
          <ul class="space-y-2 text-sm text-gray-600 flex-1">
            <li class="flex gap-2"><span class="text-brand-500">✓</span> 3 repos</li>
            <li class="flex gap-2"><span class="text-brand-500">✓</span> Private repos</li>
            <li class="flex gap-2"><span class="text-brand-500">✓</span> Custom domain</li>
            <li class="flex gap-2"><span class="text-brand-500">✓</span> No LogFast branding</li>
            <li class="flex gap-2"><span class="text-brand-500">✓</span> Email subscribers</li>
          </ul>
          <a :href="API_BASE + '/api/auth/login'" class="mt-6 block text-center bg-gray-900 hover:bg-gray-800 text-white py-2.5 rounded-lg text-sm font-semibold transition shadow-sm">Start Free Trial</a>
        </div>
        <div class="bg-white border border-gray-200 rounded-xl p-6 flex flex-col shadow-sm">
          <h3 class="font-semibold text-lg text-gray-900 mb-1">Pro</h3>
          <p class="text-sm text-gray-500 mb-4">For growing teams</p>
          <p class="text-3xl font-bold text-gray-900 mb-6">$19<span class="text-base font-normal text-gray-400">/mo</span></p>
          <ul class="space-y-2 text-sm text-gray-600 flex-1">
            <li class="flex gap-2"><span class="text-brand-500">✓</span> 10 repos</li>
            <li class="flex gap-2"><span class="text-brand-500">✓</span> Auto-generate on push</li>
            <li class="flex gap-2"><span class="text-brand-500">✓</span> In-app widget</li>
            <li class="flex gap-2"><span class="text-brand-500">✓</span> SEO optimized</li>
            <li class="flex gap-2"><span class="text-brand-500">✓</span> Priority support</li>
          </ul>
          <a :href="API_BASE + '/api/auth/login'" class="mt-6 block text-center border border-gray-300 text-gray-700 py-2.5 rounded-lg text-sm hover:border-gray-400 transition">Start Free Trial</a>
        </div>
      </div>
    </section>

    <!-- Footer -->
    <footer class="border-t border-gray-200 py-8 text-center text-sm text-gray-400">
      Built with ❤️ by a solo developer · 2026
    </footer>
  </div>
</template>

<script setup>
const API_BASE = import.meta.env.VITE_API_URL || ''
</script>
