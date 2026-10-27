import random

QUOTES = [
    {
        "quote": "Watching a great film or getting lost in a story isn’t an escape from reality—it’s an invitation to experience life more deeply.",
        "author": "Roger Ebert (adapted)",
        "category": "Cinema & Reflection",
    },
    {
        "quote": "A reader lives a thousand lives before he dies. The man who never reads lives only one.",
        "author": "George R.R. Martin",
        "category": "Literature & Discovery",
    },
    {
        "quote": "Cinema is a matter of what's in the frame and what's out. Track your moments, cherish the frames, and remember the story you lived.",
        "author": "Martin Scorsese",
        "category": "Cinema & Mindset",
    },
    {
        "quote": "Books are a uniquely portable magic. Every page you turn and every episode you finish is a milestone etched into your personal chronicle.",
        "author": "Stephen King",
        "category": "Books & Growth",
    },
    {
        "quote": "We do not remember days, we remember moments. When the month closes, you will not look back at an empty blur, but a rich gallery of everything you discovered.",
        "author": "Cesare Pavese",
        "category": "Retrospectives & Time",
    },
    {
        "quote": "The more that you read, the more things you will know. The more that you learn, the more places you will go.",
        "author": "Dr. Seuss",
        "category": "Curiosity & Exploration",
    },
    {
        "quote": "Stories are wild creatures. When you let them loose, who knows what havoc they might wreak? Cherish what moves you, log what inspires you.",
        "author": "Patrick Ness",
        "category": "Stories & Perspective",
    },
]


def get_random_quote():
    return random.choice(QUOTES)
