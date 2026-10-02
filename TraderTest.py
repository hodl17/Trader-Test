# -*- coding: utf-8 -*-
"""
Created on Wed Jan  1 20:47:11 2020

@author: devli
"""

import random
import sys

from PySide6.QtCore import Qt, QElapsedTimer, QTimer, QRegularExpression
from PySide6.QtGui import QColor, QKeySequence, QRegularExpressionValidator, QShortcut
from PySide6.QtWidgets import (
    QAbstractItemView, QApplication, QFrame, QHBoxLayout, QHeaderView, QLabel,
    QLineEdit, QMainWindow, QMessageBox, QProgressBar, QPushButton, QStackedWidget,
    QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
)


ROUNDS = {
    1: {'name': 'Easy', 'questions': 30, 'correct': 1, 'incorrect': -3, 'pass': -2},
    2: {'name': 'Decimals', 'questions': 30, 'correct': 2, 'incorrect': -1, 'pass': -1},
    3: {'name': 'Difficult Multiplication', 'questions': 15, 'correct': 2, 'incorrect': -2, 'pass': -1},
    4: {'name': 'Mix', 'questions': 15, 'correct': 2, 'incorrect': -2, 'pass': -1},
}
FULL_TEST_TARGET_SECONDS = 13 * 60
SYMBOLS = {'+': '+', '-': '−', '*': '×', '/': '÷'}

GOOD = '#3fb950'
BAD = '#f85149'
WARN = '#d29922'

STYLE = """
QWidget { background: #0f1115; color: #e6e8ec; font-size: 15px; }
QLabel { background: transparent; }
QLabel#title { font-size: 34px; font-weight: 700; }
QLabel#heading { font-size: 22px; font-weight: 700; }
QLabel#muted { color: #8b93a1; }
QLabel#question { font-size: 60px; font-weight: 600; }
QLabel#timer { font-family: Menlo, monospace; font-size: 18px; }
QLabel#statValue { font-size: 30px; font-weight: 700; }
QPushButton {
    background: #1b1f27; border: 1px solid #2a2f3a; border-radius: 10px; padding: 10px 18px;
}
QPushButton:hover { background: #222733; border-color: #3a4150; }
QPushButton:pressed { background: #161a21; }
QPushButton#primary { background: #4f8cff; border: none; color: white; font-weight: 600; }
QPushButton#primary:hover { background: #6a9dff; }
QPushButton#menuItem { text-align: left; padding: 0; }
QLineEdit#answer {
    background: #181b22; border: 2px solid #2a2f3a; border-radius: 12px;
    padding: 12px; font-size: 28px;
}
QLineEdit#answer:focus { border-color: #4f8cff; }
QFrame#card { background: #181b22; border: 1px solid #262a33; border-radius: 12px; }
QFrame#card QLabel, QFrame#card QWidget { background: transparent; }
QProgressBar { background: #1b1f27; border: none; border-radius: 3px; }
QProgressBar::chunk { background: #4f8cff; border-radius: 3px; }
QTableWidget {
    background: #181b22; border: 1px solid #262a33; border-radius: 12px; gridline-color: transparent;
}
QTableWidget::item { padding: 6px; border-bottom: 1px solid #20242d; }
QHeaderView::section {
    background: #181b22; color: #8b93a1; border: none; border-bottom: 1px solid #262a33;
    padding: 8px; font-weight: 600;
}
QScrollBar:vertical { background: transparent; width: 10px; }
QScrollBar::handle:vertical { background: #2a2f3a; border-radius: 5px; min-height: 30px; }
QScrollBar::add-line, QScrollBar::sub-line { height: 0; }
"""


def fmt(x):
    x = round(x, 2) + 0.0  # + 0.0 turns -0.0 into 0.0
    return ('%.2f' % x).rstrip('0').rstrip('.')


def fmt_time(seconds):
    return '%02d:%02d' % divmod(int(seconds), 60)


def max_points(rounds):
    return sum(ROUNDS[r]['questions'] * ROUNDS[r]['correct'] for r in rounds)


def divisor_question(low, high, excluded):
    # Hard filter: skip trivial divisors (e.g. x / 1), redrawing the numerator until one remains
    while True:
        numerator = random.randint(low, high)
        divisors = [i for i in range(2, numerator) if numerator % i == 0 and i not in excluded]
        if divisors:
            return numerator, random.choice(divisors)


def split(value):
    # Write value as "a + b" or "a − b" with a and b between 1 and 99
    if value > 98 or random.random() < 0.5:
        a = random.randint(1, value - 1)
        return '%d + %d' % (a, value - a)
    b = random.randint(1, 99 - value)
    return '%d − %d' % (value + b, b)


def generate_question(rnd):
    operations = ['+', '-', '*', '/']
    if rnd == 1:
        op = random.choice(operations)
        if op == '*':
            left, right = random.randint(1, 99), random.randint(1, 10)
            answer = left * right
        elif op == '/':
            left, right = divisor_question(2, 99, ())
            answer = left / right
        else:
            left, right = random.randint(1, 99), random.randint(1, 99)
            answer = left + right if op == '+' else left - right

    elif rnd == 2:
        op = random.choice(operations)
        if op == '*':
            left, right = random.randint(1, 99) / 100, random.randint(1, 99) / 100
            answer = left * right
        elif op == '/':
            # 100 would display as "÷ 1"
            numerator, denominator = divisor_question(2, 999, (100,))
            left, right = numerator / 100, denominator / 100
            answer = numerator / denominator
        else:
            left, right = random.randint(1000, 9999) / 100, random.randint(1000, 9999) / 100
            answer = left + right if op == '+' else left - right

    elif rnd == 3:
        op = '*'
        left = random.randint(1, 5000) / random.choice([1, 100])
        right = random.randint(1, 5000) / random.choice([1, 100])
        answer = left * right

    else:
        # (a ± b) × (c ± d) or (a ± b) ÷ (c ± d), where each bracket is a round 1 sized number
        if random.random() < 0.5:
            op, left, right = '*', random.randint(2, 99), random.randint(2, 10)
            answer = left * right
        else:
            op = '/'
            left, right = divisor_question(2, 99, ())
            answer = left / right
        return '(%s)  %s  (%s)' % (split(left), SYMBOLS[op], split(right)), answer

    return '%s  %s  %s' % (fmt(left), SYMBOLS[op], fmt(right)), answer


class Session:

    def __init__(self, rounds):
        self.rounds = rounds
        self.round_idx = 0
        self.q_num = 0
        self.history = []
        self.points = {r: 0 for r in rounds}
        self.times = {}

    @property
    def rnd(self):
        return self.rounds[self.round_idx]

    def record(self, question, answer, given):
        rules = ROUNDS[self.rnd]
        if given is None:
            delta = rules['pass']
        elif round(given, 2) == round(answer, 2):
            delta = rules['correct']
        else:
            delta = rules['incorrect']
        self.points[self.rnd] += delta
        self.history.append((self.rnd, question, answer, given, delta))
        self.q_num += 1


class MenuButton(QPushButton):

    def __init__(self, title, detail):
        super().__init__()
        self.setObjectName('menuItem')
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(62)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 10, 20, 10)
        layout.setSpacing(2)
        for text, name in ((title, ''), (detail, 'muted')):
            label = QLabel(text)
            label.setObjectName(name)
            label.setAttribute(Qt.WA_TransparentForMouseEvents)
            layout.addWidget(label)
        layout.itemAt(0).widget().setStyleSheet('font-size: 17px; font-weight: 600;')


def card(*widgets):
    frame = QFrame()
    frame.setObjectName('card')
    layout = QVBoxLayout(frame)
    layout.setContentsMargins(18, 14, 18, 14)
    layout.setSpacing(4)
    for w in widgets:
        layout.addWidget(w)
    return frame


def label(text, name='', align=None):
    w = QLabel(text)
    w.setObjectName(name)
    if align is not None:
        w.setAlignment(align)
    return w


class MenuPage(QWidget):

    def __init__(self, app):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(60, 40, 60, 40)
        layout.setSpacing(10)
        layout.addWidget(label('Trader Test', 'title'))
        layout.addWidget(label('Mental maths practice in the style of trading firm assessments.', 'muted'))
        layout.addSpacing(12)

        items = [
            ('Round 1 · Easy', '30 questions · + − × ÷ on whole numbers', lambda: app.start_test([1])),
            ('Round 2 · Decimals', '30 questions · + − × ÷ with decimals', lambda: app.start_test([2])),
            ('Round 3 · Difficult Multiplication', '15 questions · large and decimal products', lambda: app.start_test([3])),
            ('Round 4 · Mix', '15 questions · (a ± b) × (c ± d) and (a ± b) ÷ (c ± d)', lambda: app.start_test([4])),
            ('Full Test', 'All four rounds back to back · aim for 60%+ in under 13 minutes', lambda: app.start_test(list(ROUNDS))),
            ('Instructions', 'Scoring rules and how to play', app.show_instructions),
        ]
        for title, detail, action in items:
            button = MenuButton(title, detail)
            button.clicked.connect(action)
            layout.addWidget(button)
        layout.addStretch()


class InstructionsPage(QWidget):

    def __init__(self, app):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(60, 40, 60, 40)
        layout.setSpacing(14)
        layout.addWidget(label('Instructions', 'heading'))

        intro = label(
            'Type your answer and press <b>Enter</b>. Press <b>Enter</b> on an empty box to skip '
            'a question, and <b>Esc</b> to quit. Answers are checked to 2 decimal places. '
            'Negative marking is used, and the points differ in each round.', 'muted')
        intro.setWordWrap(True)
        layout.addWidget(intro)

        table = QTableWidget(len(ROUNDS), 5)
        table.setHorizontalHeaderLabels(['Round', 'Questions', 'Correct', 'Incorrect', 'Skipped'])
        for row, (rnd, rules) in enumerate(ROUNDS.items()):
            values = ['%d · %s' % (rnd, rules['name']), rules['questions'],
                      '%+d' % rules['correct'], '%+d' % rules['incorrect'], '%+d' % rules['pass']]
            for col, value in enumerate(values):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter)
                table.setItem(row, col, item)
        style_table(table)
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        table.setFixedHeight(table.horizontalHeader().height() + len(ROUNDS) * 44 + 4)
        layout.addWidget(table)

        outro = label(
            'The full test is all four rounds in a row, for a maximum of %d points. '
            'Aim to finish in under 13 minutes and score at least 60%%.' % max_points(ROUNDS), 'muted')
        outro.setWordWrap(True)
        layout.addWidget(outro)
        layout.addStretch()

        back = QPushButton('Back to menu')
        back.setObjectName('primary')
        back.clicked.connect(app.show_menu)
        layout.addWidget(back, alignment=Qt.AlignRight)


class TestPage(QWidget):

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.session = None
        self.elapsed = QElapsedTimer()
        self.round_start = 0
        self.ticker = QTimer(self)
        self.ticker.setInterval(200)
        self.ticker.timeout.connect(self.update_timer)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 28, 40, 36)
        layout.setSpacing(10)

        top = QHBoxLayout()
        self.round_label = label('', 'heading')
        self.timer_label = label('00:00', 'timer')
        quit_button = QPushButton('Quit')
        quit_button.clicked.connect(self.confirm_quit)
        top.addWidget(self.round_label)
        top.addStretch()
        top.addWidget(self.timer_label)
        top.addSpacing(16)
        top.addWidget(quit_button)
        layout.addLayout(top)

        stats = QHBoxLayout()
        self.progress_label = label('', 'muted')
        self.points_label = label('', 'muted')
        stats.addWidget(self.progress_label)
        stats.addStretch()
        stats.addWidget(self.points_label)
        layout.addLayout(stats)

        self.progress = QProgressBar()
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(6)
        layout.addWidget(self.progress)

        layout.addStretch(2)
        self.question_label = label('', 'question', Qt.AlignCenter)
        layout.addWidget(self.question_label)
        layout.addSpacing(24)

        self.answer = QLineEdit()
        self.answer.setObjectName('answer')
        self.answer.setAlignment(Qt.AlignCenter)
        self.answer.setFixedWidth(340)
        self.answer.setPlaceholderText('Your answer')
        self.answer.setValidator(QRegularExpressionValidator(QRegularExpression(r'-?\d*\.?\d*')))
        self.answer.returnPressed.connect(self.submit)
        layout.addWidget(self.answer, alignment=Qt.AlignCenter)

        buttons = QHBoxLayout()
        buttons.addStretch()
        skip = QPushButton('Skip')
        skip.clicked.connect(self.skip)
        submit = QPushButton('Submit')
        submit.setObjectName('primary')
        submit.clicked.connect(self.submit)
        for b in (skip, submit):
            b.setFixedWidth(130)
            b.setFocusPolicy(Qt.NoFocus)
            buttons.addWidget(b)
        buttons.addStretch()
        layout.addSpacing(8)
        layout.addLayout(buttons)

        layout.addStretch(3)
        layout.addWidget(label('Enter to submit  ·  Enter on empty to skip  ·  Esc to quit',
                               'muted', Qt.AlignCenter))

        shortcut = QShortcut(QKeySequence(Qt.Key_Escape), self)
        shortcut.setContext(Qt.WidgetWithChildrenShortcut)
        shortcut.activated.connect(self.confirm_quit)

    def start(self, rounds):
        self.session = Session(rounds)
        self.elapsed.start()
        self.round_start = 0
        self.ticker.start()
        self.update_timer()
        self.next_question()

    def next_question(self):
        s = self.session
        rules = ROUNDS[s.rnd]
        if s.q_num == rules['questions']:
            now = self.elapsed.elapsed() / 1000
            s.times[s.rnd] = now - self.round_start
            if s.round_idx + 1 == len(s.rounds):
                self.ticker.stop()
                self.app.show_results(s, now)
                return
            s.round_idx += 1
            s.q_num = 0
            self.round_start = now
            rules = ROUNDS[s.rnd]

        self.question, self.correct = generate_question(s.rnd)
        self.round_label.setText('Round %d · %s' % (s.rnd, rules['name']))
        self.progress_label.setText('Question %d of %d' % (s.q_num + 1, rules['questions']))
        self.points_label.setText('Points: %d' % sum(s.points.values()))
        self.progress.setMaximum(rules['questions'])
        self.progress.setValue(s.q_num)
        self.question_label.setText(self.question)
        self.question_label.setStyleSheet('font-size: %dpx;' % (60 if len(self.question) <= 20 else 44))
        self.answer.clear()
        self.answer.setFocus()

    def submit(self):
        text = self.answer.text()
        if text == '':
            self.skip()
            return
        try:
            given = float(text)
        except ValueError:  # partial input such as "-" or "."
            return
        self.session.record(self.question, self.correct, given)
        self.next_question()

    def skip(self):
        self.session.record(self.question, self.correct, None)
        self.next_question()

    def update_timer(self):
        seconds = self.elapsed.elapsed() / 1000
        self.timer_label.setText(fmt_time(seconds))
        if len(self.session.rounds) > 1 and seconds > FULL_TEST_TARGET_SECONDS:
            self.timer_label.setStyleSheet('color: %s;' % WARN)
        else:
            self.timer_label.setStyleSheet('')

    def confirm_quit(self):
        reply = QMessageBox.question(self, 'Quit test', 'Quit this test? Your progress will be lost.')
        if reply == QMessageBox.Yes:
            self.ticker.stop()
            self.app.show_menu()
        else:
            self.answer.setFocus()


class ResultsPage(QWidget):

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.rounds = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 32, 40, 32)
        layout.setSpacing(14)
        layout.addWidget(label('Results', 'heading'))

        self.cards = QHBoxLayout()
        self.cards.setSpacing(12)
        layout.addLayout(self.cards)

        layout.addWidget(label('Question breakdown', 'muted'))
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(['Round', 'Question', 'Correct answer', 'Your answer', 'Points'])
        style_table(self.table)
        layout.addWidget(self.table, 1)

        buttons = QHBoxLayout()
        buttons.addStretch()
        menu = QPushButton('Back to menu')
        menu.clicked.connect(app.show_menu)
        retry = QPushButton('Try again')
        retry.setObjectName('primary')
        retry.clicked.connect(lambda: app.start_test(self.rounds))
        buttons.addWidget(menu)
        buttons.addWidget(retry)
        layout.addLayout(buttons)

    def show_session(self, session, total_time):
        self.rounds = session.rounds

        while self.cards.count():
            self.cards.takeAt(0).widget().deleteLater()
        summaries = [('Round %d' % r, session.points[r], max_points([r]), session.times[r])
                     for r in session.rounds]
        if len(session.rounds) > 1:
            summaries.append(('Total', sum(session.points.values()), max_points(session.rounds), total_time))
        for title, points, maximum, seconds in summaries:
            percent = int(points / maximum * 100)
            value = label('%d / %d' % (points, maximum), 'statValue')
            value.setStyleSheet('color: %s;' % (GOOD if percent >= 60 else BAD if percent < 0 else '#e6e8ec'))
            self.cards.addWidget(card(label(title, 'muted'), value,
                                      label('%d%%  ·  %s' % (percent, fmt_time(seconds)), 'muted')))

        self.table.setRowCount(len(session.history))
        for row, (rnd, question, answer, given, delta) in enumerate(session.history):
            values = [str(rnd), question, fmt(answer), '—' if given is None else fmt(given), '%+d' % delta]
            for col, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignCenter)
                if col == 4:
                    item.setForeground(QColor(GOOD if delta > 0 else BAD))
                self.table.setItem(row, col, item)
        self.table.scrollToTop()


def style_table(table):
    table.verticalHeader().hide()
    table.setShowGrid(False)
    table.setFocusPolicy(Qt.NoFocus)
    table.setSelectionMode(QAbstractItemView.NoSelection)
    table.setEditTriggers(QAbstractItemView.NoEditTriggers)
    table.verticalHeader().setDefaultSectionSize(44)
    table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)


class TraderTest(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Trader Test')
        self.resize(860, 660)
        self.setMinimumSize(720, 560)

        self.stack = QStackedWidget()
        self.menu = MenuPage(self)
        self.instructions = InstructionsPage(self)
        self.test = TestPage(self)
        self.results = ResultsPage(self)
        for page in (self.menu, self.instructions, self.test, self.results):
            self.stack.addWidget(page)
        self.setCentralWidget(self.stack)

    def show_menu(self):
        self.stack.setCurrentWidget(self.menu)

    def show_instructions(self):
        self.stack.setCurrentWidget(self.instructions)

    def start_test(self, rounds):
        self.stack.setCurrentWidget(self.test)
        self.test.start(rounds)

    def show_results(self, session, total_time):
        self.results.show_session(session, total_time)
        self.stack.setCurrentWidget(self.results)


def program():
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLE)
    window = TraderTest()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    program()
