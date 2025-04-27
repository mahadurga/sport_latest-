import random
import logging

logger = logging.getLogger(__name__)

# Commentary templates for different cricket events
COMMENTARY_TEMPLATES = {
    "boundary": {
        "four": [
            "That's a beautiful shot! The ball races away to the boundary for FOUR!",
            "What a stroke! That's FOUR runs as the ball reaches the boundary rope.",
            "Expertly placed! The fielder has no chance as the ball speeds to the boundary for FOUR.",
            "That'll be FOUR! Perfectly timed and placed to the boundary.",
            "The batsman finds the gap and gets FOUR runs for that shot."
        ],
        "six": [
            "MASSIVE HIT! That's gone all the way for SIX!",
            "The batsman has really got hold of that one! SIX runs!",
            "Up, up, and away! That's a huge SIX over the boundary!",
            "What a strike! The ball sails over the boundary for SIX!",
            "The crowd is on their feet! That's a magnificent SIX!"
        ]
    },
    "wicket": {
        "bowled": [
            "BOWLED HIM! The stumps are shattered!",
            "The ball hits the timber! He's BOWLED!",
            "Clean bowled! The batsman has to go!",
            "The stumps are in disarray! That's a brilliant delivery to get the wicket!",
            "The ball sneaks through the gate and hits the stumps! He's out!"
        ],
        "caught": [
            "CAUGHT! The fielder takes a good catch and the batsman has to walk!",
            "Up goes the ball... and it's CAUGHT! What a take by the fielder!",
            "That's a catch! The batsman is disappointed as he walks back to the pavilion.",
            "The ball goes straight to the fielder, who makes no mistake! CAUGHT!",
            "A simple catch but an important wicket! The batsman is out!"
        ],
        "lbw": [
            "That looks plumb! The umpire raises the finger for LBW!",
            "Appeal for LBW... and he's given! The batsman has to go!",
            "Struck on the pads, and the umpire agrees with the appeal! LBW!",
            "A huge appeal for LBW, and the umpire doesn't hesitate! He's out!",
            "The ball strikes the pad in line with the stumps. LBW! He's gone!"
        ],
        "run_out": [
            "The fielder hits the stumps directly! That's a RUN OUT!",
            "There was never a run there! The batsman is RUN OUT!",
            "Quick work by the fielder! The batsman is well short of his ground. RUN OUT!",
            "The throw is accurate, and the batsman is RUN OUT!",
            "Brilliant fielding! The batsman is caught short of the crease. RUN OUT!"
        ],
        "stumped": [
            "The batsman is out of his crease, and the keeper whips off the bails! STUMPED!",
            "Clever work by the wicketkeeper! The batsman is STUMPED!",
            "The batsman overbalances, and the keeper is quick to remove the bails! STUMPED!",
            "Sharp stumping by the keeper! The batsman has to go!",
            "The batsman is caught short of his ground, and the keeper completes the stumping!"
        ]
    },
    "shot_played": {
        "straight drive": [
            "That's a classic straight drive! A classic shot played with a straight bat, hitting the ball back past the bowler.",
            "The batsman plays a lovely straight drive. Well-timed and executed.",
            "Excellent execution of the straight drive!",
            "Textbook straight drive from the batsman!",
            "The batsman demonstrates a perfect straight drive. The hallmark of good technique."
        ],
        "cover drive": [
            "What a glorious cover drive! The footwork is immaculate, and the timing is absolutely perfect.",
            "That's pure elegance! A masterful cover drive, straight out of the coaching manual.",
            "Beautiful cover drive! The way the batsman leans into the shot is a sight to behold.",
            "Picture-perfect cover drive! The balance, the timing, the placement - it's all there.",
            "Exquisite cover drive! You won't see a better example of this classical cricket shot."
        ],
        "cut shot": [
            "That's a classic cut shot! A horizontal bat shot played to a short, wide delivery, cutting the ball toward point.",
            "The batsman plays a lovely cut shot. Taking advantage of the width offered.",
            "Excellent execution of the cut shot!",
            "Textbook cut shot from the batsman!",
            "The batsman demonstrates a perfect cut shot. Using the pace of the ball well."
        ],
        "pull shot": [
            "What an exceptional pull shot! The batsman rocks back quickly, picking up the length early and executing a powerful shot to the leg side.",
            "That's a magnificent pull shot! Watch how the batsman pivots into position, getting right on top of the bounce before dispatching it.",
            "Brilliant pull shot execution! The way the batsman picks up the length and swivels into position shows years of practice.",
            "Classic pull shot mastery on display! Look at the balance and poise as the batsman rocks back.",
            "Textbook pull shot perfection! The quick footwork, the precise head position - absolutely clinical execution!"
        ],
        "hook shot": [
            "That's a classic hook shot! Similar to the pull but played to a higher bouncing ball, hooking it around to the leg side.",
            "The batsman plays a lovely hook shot. Taking on the bouncer with confidence.",
            "Excellent execution of the hook shot!",
            "Textbook hook shot from the batsman!",
            "The batsman demonstrates a perfect hook shot. Handling the short ball with aplomb."
        ],
        "sweep shot": [
            "Expertly played sweep shot! Getting down on one knee and sweeping with perfect control.",
            "Brilliant sweep! The batsman shows great technique, getting right to the pitch of the ball.",
            "Masterful sweep shot! Using the pace of the ball and placing it perfectly.",
            "Excellent sweep! The way the batsman gets down and executes the shot is textbook.",
            "Perfect sweep shot! Great technique on display, making it look effortless."
        ],
        "defensive shot": [
            "That's a classic defensive shot! A defensive stroke played with a straight bat to block the ball.",
            "The batsman plays a solid defensive shot. Showing good technique.",
            "Excellent execution of the defensive shot!",
            "Textbook defensive technique from the batsman!",
            "The batsman demonstrates perfect defensive technique. Safety first."
        ],
        "flick shot": [
            "Brilliant flick shot! The wristwork is exceptional, turning the ball from middle stump to the leg side.",
            "Masterful flick! The timing and placement show incredible skill and control.",
            "Delicate flick shot! The batsman's wrists do all the work, guiding the ball into the gap.",
            "Beautiful flick! The way the batsman uses his wrists to work the ball is pure artistry.",
            "Magnificent flick shot! The control and precision are remarkable."
        ],
        "helicopter_shot": [
            "Incredible helicopter shot! The wrist work and follow-through are absolutely spectacular.",
            "What an amazing helicopter shot! The batsman rotates the bat through 360 degrees with perfect control.",
            "Brilliant execution of the helicopter shot! The timing and balance are phenomenal.",
            "Spectacular helicopter shot! The full rotation of the bat after contact is a sight to behold.",
            "Masterful helicopter shot! The modern-day cricket shot played to perfection."
        ],
        "generic": [
            "The batsman plays a good shot there.",
            "Well played by the batsman.",
            "That's good batting technique on display.",
            "The batsman gets into position nicely to play that shot.",
            "A confident stroke from the batsman."
        ]
    }
}

# Commentary transition phrases
TRANSITIONS = {
    'en': [
        'Meanwhile, ', 'What a moment! ', 'Incredible display! ', 'The crowd goes wild as ',
        'A delightful shot! ', 'Brilliant execution! ', 'With perfect timing, ', 'Expertly played! '
    ],
    'ta': [
        'இதற்கிடையில், ', 'என்ன அருமையான தருணம்! ', 'அற்புதமான ஆட்டம்! ', 
        'பார்வையாளர்கள் ஆர்வமாக உள்ளனர்! ', 'அருமையான ஷாட்! ',
        'திறமையான ஆட்டம்! ', 'சரியான நேரத்தில்! ', 'நேர்த்தியாக ஆடினார்! '
    ],
    'hi': ['इस बीच, ', 'क्या पल है! ', 'अद्भुत प्रदर्शन! ', 'दर्शक उत्साहित हैं जब ']
}

# Match situation commentary
MATCH_SITUATION = [
    "The pressure is mounting on the batting side.",
    "The bowler seems confident after that delivery.",
    "The batsman needs to be more careful with those shots.",
    "The field placement is really testing the batsman's patience.",
    "The bowling side is looking for a breakthrough here.",
    "The batting team is looking to build a partnership.",
    "Both teams know how crucial this phase of play is.",
    "The run rate is slowly climbing up.",
    "The captain is considering a bowling change.",
    "The fielders are alert and ready for any chance."
]

# Tamil commentary templates
TAMIL_TEMPLATES = {
    "transitions": [
        "இதற்கிடையில், ", 
        "என்ன அருமையான தருணம்! ", 
        "அற்புதமான ஆட்டம்! ", 
        "பார்வையாளர்கள் உற்சாகமாக உள்ளனர்! ", 
        "நேர்த்தியான ஆட்டம்! "
    ],
    "shot_played": {
        "generic": [
            "பேட்ஸ்மேன் நிலையை சரியாக அமைத்து பந்தை ஆடுகிறார்",
            "அழகான பேட்டிங் நுட்பம் காட்டுகிறார்",
            "பந்தை திறமையாக ஆடுகிறார்",
            "சிறப்பான ஷாட் ஆட்டம்!"
        ],
        "cover_drive": [
            "அழகான கவர் டிரைவ் ஷாட்! திறமையான ஆட்டம்!",
            "கவர் பகுதியில் அற்புதமான ஷாட்!"
        ],
        "straight_drive": [
            "நேர்கோட்டில் அழகான ஷாட்! மைதானத்தின் நடுவில் செல்கிறது!",
            "நேரான ஷாட்! பந்து வேகமாக செல்கிறது!"
        ]
    },
    "boundary": {
        "four": [
            "பந்து பவுண்டரிக்கு சென்று நான்கு ரன்கள்!",
            "அற்புதமான ஷாட்! பந்து எல்லைக் கோட்டை கடந்து நான்கு ரன்கள்!",
            "நேர்த்தியான ஆட்டம்! பவுண்டரிக்கு நான்கு ரன்கள்!"
        ],
        "six": [
            "அற்புதமான ஷாட்! பந்து மைதானத்தை விட்டு வெளியேறி ஆறு ரன்கள்!",
            "பேட்ஸ்மேனின் சிறந்த ஷாட்! பந்து வானில் பறந்து ஆறு ரன்கள்!",
            "வலுவான ஷாட்! பந்து மைதானத்தை தாண்டி ஆறு ரன்கள்!"
        ]
    }
}

def generate_commentary(events, language='en'):
    """
    Generate commentary based on detected events with language support.
    Args:
        events: List of detected events
        language: Language code ('en', 'hi', 'ta', etc.)
    """
    commentary_parts = []

    if language == 'ta':
        for event in events:
            commentary_parts.append(random.choice(TAMIL_TEMPLATES["transitions"]))

            if event['type'] == 'shot_played':
                shot_type = event.get('subtype', 'generic')
                templates = TAMIL_TEMPLATES["shot_played"].get(shot_type, TAMIL_TEMPLATES["shot_played"]["generic"])
                commentary_parts.append(random.choice(templates))
            elif event['type'] == 'boundary':
                boundary_type = event.get('subtype', 'four')
                templates = TAMIL_TEMPLATES["boundary"][boundary_type]
                commentary_parts.append(random.choice(templates))

        if not commentary_parts:
            return "பேட்ஸ்மேன் கிரீஸில் நிற்கிறார், ஆட்டம் தொடங்க உள்ளது."
    else:
        prev_event_type = None
        for event in events:
            if event['type'] == 'shot_played':
                shot_type = event.get('subtype', 'generic')
                templates = COMMENTARY_TEMPLATES["shot_played"].get(shot_type, COMMENTARY_TEMPLATES["shot_played"]["generic"])
                transition = random.choice(TRANSITIONS['en'])
                commentary_parts.append(f"{transition}{random.choice(templates)}")
            elif event['type'] == 'boundary':
                boundary_type = event.get('subtype', 'four')
                boundary_desc = random.choice(COMMENTARY_TEMPLATES["boundary"][boundary_type])
                commentary_parts.append(boundary_desc)
            prev_event_type = event['type']

    if not commentary_parts:
        default_commentary = {
            'en': "The batsman takes guard as the tension builds in the stadium. The crowd waits in anticipation.",
            'hi': "बल्लेबाज गार्ड लेते हैं और स्टेडियम में तनाव बढ़ता है। दर्शक उत्सुकता से प्रतीक्षा करते हैं।",
            'ta': "பேட்ஸ்மேன் கார்டு எடுக்கிறார், மைதானத்தில் பதற்றம் அதிகரிக்கிறது. பார்வையாளர்கள் ஆவலுடன் காத்திருக்கின்றனர்."
        }
        return default_commentary.get(language, default_commentary['en'])

    return ' '.join(commentary_parts)