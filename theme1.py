"""Theme 1 (15 days): 'A Father's First SIP'. Generates stories, feed posts, reels."""
import os, math, random, subprocess, shutil, sys
from PIL import Image, ImageDraw
import ig_gen as g

W, H = 1080, 1920
BG = (17, 17, 17); WH = (255, 255, 255); GR = (150, 150, 150); LT = (210, 210, 210)
os.makedirs("stories/theme1", exist_ok=True)
os.makedirs("posts/theme1", exist_ok=True)
os.makedirs("reels/theme1", exist_ok=True)

# ---------------- stories (16:00 IST) ----------------
EP = [
    "“Papa, when I grow up, I want to study abroad.”",
    "“Beta, a big goal needs a small start. Let us begin this month.”",
    "“One SIP date. One small step every month. That is how it begins.”",
    "“Will it be enough?” “No one can promise that. We can only stay regular.”",
    "“Why the same date every month, Papa?” “Because habit matters more than mood.”",
    "“In my time we saved in a steel almirah.” “Now we plan on purpose, Dada.”",
    "“Let us write our goals down: school fees, a family trip, an emergency fund.”",
    "“The news says markets are down today.” “Our plan was made for days like this.”",
    "“Can we skip this month?” “Let us read our plan first, not the headlines.”",
    "“First an emergency fund. Then the long-term goals.”",
    "“How long will it take?” “Long goals need patience, beta.”",
    "“Papa, I drew a jar for each of our goals.”",
    "“Why not put everything in one place?” “We spread our money and know what we hold.”",
    "“We review the plan on set dates. Not every time the news changes.”",
    "“Thank you for starting, Papa.” “Start. Stay. Review. That is the whole story.”",
]
for i, t in enumerate(EP, 1):
    g.story_quote(f"stories/theme1/ep{i:02d}.png", t,
                  f"A FAMILY STORY · EPISODE {i} · ILLUSTRATIVE")

# ---------------- feed posts (09:00 IST) ----------------
POSTS = {
    1: ("Start with DDS", "How to begin your SIP journey", [
        ("01", "Define the goal", "Home, education, retirement. Name it and set a time horizon."),
        ("02", "Complete one-time KYC", "A pre-requisite before investing in mutual funds. We guide you."),
        ("03", "Pick an amount you can sustain", "Choose a monthly SIP amount and date that fit your budget."),
        ("04", "Review on a schedule", "Revisit your plan periodically, not every time markets move.")],
        "Start with a plan. Stay with a process."),
    2: ("Know the difference", "SIP or lump sum?", [
        ("01", "SIP", "A fixed amount invested in a scheme at regular intervals."),
        ("02", "Lump sum", "One amount invested at one time."),
        ("03", "Both carry market risk", "Choose the method you can stay with through all conditions.")],
        "Method matters. Discipline matters more."),
    4: ("Before you begin", "Four questions before you invest", [
        ("01", "What is the goal?", "School fees, a home, retirement. Be specific."),
        ("02", "When is it needed?", "Put a year next to every goal."),
        ("03", "How much fall can you stay calm through?", "Know your comfort before markets test it."),
        ("04", "Is your emergency fund in place?", "Keep it separate from long-term goals.")],
        "Answer first. Invest after."),
    5: ("Discipline", "Habit over timing", [
        ("01", "Choose a date", "Pick a SIP date that suits your monthly cash flow."),
        ("02", "Automate it", "Let a standing instruction run, so mood does not decide."),
        ("03", "Review on set dates", "Look at the plan on schedule, not on every headline.")],
        "Discipline is a decision made in advance."),
    7: ("Goal planning", "Match each goal to a timeline", [
        ("01", "List your goals", "Write down every goal, big or small."),
        ("02", "Put a date on each", "The year you need the money shapes the plan."),
        ("03", "Match risk to the date", "Money needed soon has little time to recover from a fall.")],
        "Every rupee gets a goal and a date."),
    8: ("Before you invest", "Check these three things", [
        ("01", "KYC", "A pre-requisite before investing in mutual funds."),
        ("02", "The risk-o-meter", "Mutual funds display a risk level for each scheme. Read it."),
        ("03", "Scheme related documents", "Read them carefully before you invest.")],
        "Informed first. Invested later."),
    10: ("Basics first", "Safety before goals", [
        ("01", "Emergency fund", "Keep money for unexpected needs separate from long-term goals."),
        ("02", "Then long-term goals", "Invest for long goals once the basics are covered."),
        ("03", "Revisit as life changes", "A new job, a new child, a new goal. Update the plan.")],
        "A calm plan starts with a safety net."),
    11: ("Discipline", "Plan, not news", [
        ("01", "News changes daily", "A plan is built to last through many news cycles."),
        ("02", "Set review dates", "Choose when you will review. Stick to it."),
        ("03", "Change for reasons, not moods", "Update the plan when your goals change.")],
        "Decide calmly. Act on the plan."),
    13: ("Your one-page plan", "Write it down", [
        ("01", "Goal", "What are you investing for?"),
        ("02", "Timeline", "By which year do you need it?"),
        ("03", "SIP amount and date", "What can you sustain every month?"),
        ("04", "Review dates", "When will you check progress?")],
        "A plan on paper beats a plan in the mood."),
    14: ("About us", "Who we are", [
        ("01", "AMFI-registered Mutual Fund Distributor", "ARN-359084. We help you invest in mutual fund schemes."),
        ("02", "What we are not", "Not a SEBI-registered investment adviser or research analyst."),
        ("03", "What we offer", "Education, process and support. No tips and no return promises.")],
        "Know who you are talking to."),
}
for day, (eb, title, items, tag) in POSTS.items():
    g.feed_checklist(f"posts/theme1/day{day:02d}.png", eb, title, items, tag)


# ---------------- reels (09:00 IST on days 3,6,9,12,15) ----------------
def chrome(d, month_label=None):
    g.tracked(d, (80, 280), "DDS CAPITAL WEALTH", g.MM(24), WH)
    d.line([(80, 322), (W - 80, 322)], fill=WH, width=2)


def foot(d, note):
    d.text((80, 1560), note, font=g.MR(15), fill=GR)
    g.footer(d, W, 1600, fg=WH, sub=(150, 150, 150))


ONLY = os.environ.get("ONLY", "").split(",") if os.environ.get("ONLY") else None
def render(name, nframes, drawfn):
    if ONLY and name not in ONLY: return
    d_ = f"/tmp/fr_{name}"
    shutil.rmtree(d_, ignore_errors=True); os.makedirs(d_)
    for fi in range(nframes):
        img = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(img)
        chrome(d)
        drawfn(d, fi / 25.0)
        img.save(f"{d_}/f{fi:04d}.png")
    out = f"reels/theme1/{name}.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", "25", "-i", f"{d_}/f%04d.png",
                    "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-shortest",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "21", "-c:a", "aac",
                    "-movflags", "+faststart", out], check=True)
    shutil.rmtree(d_, ignore_errors=True)


NOTE = "Illustrative animation. Not a projection of returns."

# V1: SIP jar
jl, jr, jt, jb, R = 330, 750, 720, 1330, 44
def jpos(i):
    r, c = divmod(i, 4); return (jl + 24 + R + c * (2 * R + 4), jb - 14 - R - r * (2 * R - 2))
def coin(d, x, y):
    d.ellipse([x-R, y-R, x+R, y+R], fill=WH, outline=(200, 200, 200), width=3)
    d.ellipse([x-R+10, y-R+10, x+R-10, y+R-10], outline=BG, width=3)
    f = g.SB(46); w = d.textlength("₹", font=f); d.text((x - w/2, y - 30), "₹", font=f, fill=BG)
def jar(d):
    d.line([(jl, jt), (jl, jb-30), (jl+30, jb), (jr-30, jb), (jr, jb-30), (jr, jt)], fill=WH, width=6, joint="curve")
    d.line([(jl-20, jt), (jr+20, jt)], fill=WH, width=6)
def v1(d, t):
    M_ = 0.75
    m = min(12, int(t / M_) + 1)
    d.text((80, 420), "MONTH %02d" % m, font=g.MM(54), fill=WH)
    d.text((80, 500), "One SIP date. Every month.", font=g.SI(40), fill=LT)
    jar(d)
    for i in range(12):
        t0 = i * M_
        if t < t0: break
        px, py = jpos(i); k = (t - t0) / 0.35
        coin(d, px, (560 + (py - 560) * k * k) if k < 1 else py)
    jar(d)
    if t > 12 * M_ + 0.4:
        c = int(255 * min(1, (t - 12 * M_ - 0.4) / 0.6))
        d.text((80, 1420), "Small, regular steps.", font=g.SI(56), fill=(c, c, c))
    foot(d, NOTE)
render("v1_sip_jar", int((12 * 0.75 + 3) * 25), v1)

# V2: calendar flip
MON = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
def v2(d, t):
    P = 0.8
    d.text((80, 420), "THE SIP DATE", font=g.MM(54), fill=WH)
    d.text((80, 500), "Same date. Every month.", font=g.SI(40), fill=LT)
    cx0, cy0, cx1, cy1 = 240, 640, 840, 1240
    d.rectangle([cx0, cy0, cx1, cy1], outline=WH, width=6)
    d.rectangle([cx0, cy0, cx1, cy0 + 130], fill=WH)
    m = min(11, int(t / P)); k = (t - m * P) / P if t < 12 * P else 1
    mf = g.MM(70); ml = MON[m]
    d.text((540 - d.textlength(ml, font=mf) / 2, cy0 + 28), ml, font=mf, fill=BG)
    df = g.SB(300); dt = "05"
    slide = 0 if k > 0.25 else (1 - k / 0.25) * 80
    d.text((540 - d.textlength(dt, font=df) / 2, cy0 + 170 + slide), dt, font=df, fill=WH)
    if t < 12 * P and k > 0.45 or t >= 12 * P:
        d.line([(690, 1160), (725, 1195), (790, 1125)], fill=WH, width=10, joint="curve")
    done = min(12, int(t / P) + (1 if k > 0.45 else 0))
    for i in range(12):
        x = 140 + i * 72
        d.ellipse([x, 1300, x + 36, 1336], fill=WH if i < done else None, outline=WH, width=3)
    if t > 12 * P + 0.3:
        c = int(255 * min(1, (t - 12 * P - 0.3) / 0.6))
        d.text((80, 1420), "Habit, not mood.", font=g.SI(56), fill=(c, c, c))
    foot(d, NOTE)
render("v2_calendar", int((12 * 0.8 + 3) * 25), v2)

# V3: goal map
GOALS = ["SCHOOL FEES", "FAMILY TRIP", "EMERGENCY FUND", "RETIREMENT"]
def v3(d, t):
    d.text((80, 420), "EVERY RUPEE", font=g.MM(54), fill=WH)
    d.text((80, 500), "Gets a goal and a date.", font=g.SI(40), fill=LT)
    for i, gl in enumerate(GOALS):
        y = 680 + i * 190; t0 = 1.0 + i * 1.8
        on = t >= t0
        a = min(1, (t - t0) / 0.5) if on else 0
        fill = (int(255 * a),) * 3
        d.rectangle([80, y, W - 80, y + 140], outline=WH, width=4, fill=fill if on else None)
        tc = BG if a > 0.5 else WH
        d.text((120, y + 38), gl, font=g.MM(44), fill=tc)
    if t > 1.0 + 4 * 1.8 + 0.3:
        c = int(255 * min(1, (t - 1.0 - 4 * 1.8 - 0.3) / 0.6))
        d.text((80, 1470), "Write yours down.", font=g.SI(56), fill=(c, c, c))
    foot(d, "Illustrative. Goals and years are examples only.")
render("v3_goals", int((1.0 + 4 * 1.8 + 3) * 25), v3)

# V4: markets move, your SIP date does not
random.seed(7)
pts = []
for i in range(60):
    taper = math.sin(math.pi * i / 59)
    pts.append(math.sin(2 * math.pi * 2.5 * i / 59) * 150 + (math.sin(i / 1.7) * 55 + random.uniform(-40, 40)) * taper)
def v4(d, t):
    d.text((80, 420), "MARKETS MOVE.", font=g.MM(54), fill=WH)
    d.text((80, 500), "Your plan stays on schedule.", font=g.SI(40), fill=LT)
    x0, x1, yc = 100, W - 100, 960
    n = int(min(1, t / 8.0) * (len(pts) - 1))
    prev = None
    for i in range(n + 1):
        x = x0 + (x1 - x0) * i / (len(pts) - 1); y = yc - pts[i]
        if prev: d.line([prev, (x, y)], fill=WH, width=5)
        prev = (x, y)
    for k in range(12):
        x = x0 + (x1 - x0) * k / 11
        if x0 + (x1 - x0) * n / (len(pts) - 1) >= x:
            d.ellipse([x - 12, 1250, x + 12, 1274], fill=WH)
    d.text((100, 1300), "SIP DATES", font=g.MM(26), fill=LT)
    if t > 8.3:
        c = int(255 * min(1, (t - 8.3) / 0.6))
        d.text((80, 1420), "Plan the steps. Not the swings.", font=g.SI(50), fill=(c, c, c))
    foot(d, "Abstract illustration. Not actual market data or a projection.")
render("v4_steady", int((8.3 + 3) * 25), v4)

# V5: start stay review
WORDS = ["START.", "STAY.", "REVIEW."]
def v5(d, t):
    d.text((80, 420), "THE WHOLE STORY", font=g.MM(54), fill=WH)
    for i, w in enumerate(WORDS):
        t0 = 0.8 + i * 1.6
        if t < t0: continue
        a = min(1, (t - t0) / 0.5); c = int(255 * a)
        y = 700 + i * 220 + int((1 - a) * 40)
        d.text((80, y), w, font=g.SB(150), fill=(c, c, c))
        wlen = d.textlength(w, font=g.SB(150))
        d.line([(80, y + 175), (80 + wlen * a, y + 175)], fill=(c, c, c), width=5)
    if t > 0.8 + 3 * 1.6 + 0.3:
        c = int(255 * min(1, (t - 0.8 - 4.8 - 0.3) / 0.6))
        d.text((80, 1440), "A family story · Theme 1 complete.", font=g.SI(40), fill=(c, c, c))
    foot(d, "Illustrative. Educational only.")
render("v5_wrap", int((0.8 + 4.8 + 3.5) * 25), v5)
print("done")
