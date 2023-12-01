import sys
import psycopg2
import environs

from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QTextEdit,
    QVBoxLayout,
    QPushButton,
    QWidget,
)

env = environs.Env()
env.read_env()


class DatabaseApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Database App')
        self.setGeometry(100, 100, 800, 600)

        self.connection = None
        self.cursor = None

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.create_table()

        sql_queries = [
            "SELECT * FROM academics ORDER BY LENGTH(full_name);",
            "SELECT REPLACE(full_name, ' ', '') AS new_name FROM academics;",
            "SELECT full_name, POSITION('ов' IN full_name) AS position_ov FROM academics;",
            "SELECT full_name, RIGHT(specialization, 2) AS two_letters FROM academics;",
            "SELECT DISTINCT specialization, REVERSE(specialization) AS reversed_specialization FROM academics;",
            "SELECT REPEAT('Какая-то фамилия ', 2) AS repeated_name;",
            "SELECT DATE '2023-12-31' - CURRENT_DATE AS days;",
            "SELECT specialization, CASE WHEN LENGTH(specialization) > 10 THEN 'длинный' ELSE 'короткий' END AS status FROM academics GROUP BY specialization;",
        ]

        for index, query in enumerate(sql_queries):
            button = QPushButton(f'Запрос {index}')
            button.clicked.connect(lambda checked, q=query: self.execute_query(q))
            layout.addWidget(button)

        self.result_widget = QTextEdit()
        layout.addWidget(self.result_widget)

        self.error_widget = QTextEdit()
        self.error_widget.setStyleSheet('color: red;')
        layout.addWidget(self.error_widget)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def connect_to_database(self):
        try:
            self.connection = psycopg2.connect(
                database=env.str('POSTGRES_DB'),
                user=env.str('POSTGRES_USER'),
                password=env.str('POSTGRES_PASSWORD'),
                host=env.str('POSTGRES_HOST'),
                port=env.str('POSTGRES_PORT'),
            )
            self.cursor = self.connection.cursor()
        except Exception as e:
            self.show_error(f'Error connecting to the database: {e}')

    def create_table(self):
        try:
            self.connect_to_database()
            create_table_query = """
                CREATE TABLE IF NOT EXISTS academics (
                    id SERIAL PRIMARY KEY,
                    full_name TEXT NOT NULL,
                    birth_date DATE NOT NULL,
                    specialization TEXT NOT NULL,
                    year_rank_assignment INT NOT NULL
                );
            """
            self.cursor.execute(create_table_query)
            self.connection.commit()
        except Exception as e:
            self.show_error(f"Error creating table: {e}")

    def execute_query(self, query: str):
        if not self.cursor:
            self.connect_to_database()

        try:
            self.cursor.execute(query)
            result = self.cursor.fetchall()
            self.show_result(result)
        except Exception as e:
            self.show_error(f'Error executing query: {e}')

    def show_result(self, result):
        formatted_result = '\n'.join([str(row) for row in result])
        self.result_widget.setPlainText(formatted_result)

    def show_error(self, error_message):
        self.error_widget.setPlainText(error_message)

    def closeEvent(self, event):
        if self.connection:
            self.connection.close()
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DatabaseApp()
    window.show()
    sys.exit(app.exec())
