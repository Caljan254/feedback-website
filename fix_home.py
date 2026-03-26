import os

carousel_overlay = """
                <!-- Text Overlay - Positioned at bottom left corner touching both edges -->
                <div class="carousel-overlay">
                    <div class="carousel-content">
                        <p
                            class="text-white text-sm sm:text-base md:text-lg font-medium mb-3 sm:mb-4 leading-relaxed max-w-2xl">
                            Driving Innovation Through ICT: Empowering students, staff, and the community with reliable
                            technology and forward-thinking digital solutions.
                        </p>
                        <div class="flex flex-col sm:flex-row gap-3">
                            <a href="/services"
                                class="bg-green-600 hover:bg-green-700 text-white px-4 sm:px-6 py-2 sm:py-3 rounded-lg font-semibold transition-all duration-300 transform hover:scale-105 text-sm sm:text-base flex items-center justify-center shadow-lg hover:shadow-xl">
                                <i class="fas fa-cogs mr-2"></i> Explore Our Services
                            </a>
                            <a href="/contact"
                                class="bg-blue-600 hover:bg-blue-700 text-white px-4 sm:px-6 py-2 sm:py-3 rounded-lg font-semibold transition-all duration-300 transform hover:scale-105 text-sm sm:text-base flex items-center justify-center shadow-lg hover:shadow-xl">
                                <i class="fas fa-headset mr-2"></i> Contact ICT Support
                            </a>
                        </div>
                    </div>
                </div>
"""

home_path = r'c:\Users\User\Downloads\seku-feedback-mng-sytem\frontend\src\components\pages\home.html'

with open(home_path, 'r', encoding='utf-8') as f:
    text = f.read()

# Insert carousel overlay if not present
if 'carousel-overlay' not in text:
    text = text.replace('loading="eager" />\n            </div>', 'loading="eager" />\n' + carousel_overlay + '            </div>')

# Remove "How It Works" section if present
# It starts at <!-- NEW: How It Works Section --> and ends with </section>

import re
text = re.sub(r'<!-- NEW: How It Works Section -->[\s\S]*?</section>', '', text)

# We already removed stats and FAQ earlier, so they should be gone. Let's just double check.
text = re.sub(r'<section class="max-w-6xl mx-auto px-4 py-8 sm:py-12 reveal">[\s\S]*?Frequently Asked Questions[\s\S]*?</section>', '', text)

with open(home_path, 'w', encoding='utf-8') as f:
    f.write(text)
    
print("home.html completely fixed!")
