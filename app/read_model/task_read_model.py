from app import db

class TaskReadModel(db.Model):
    __tablename__ = 'tasks_read'
    id = db.Column(db.String(36), primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    version = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f'<TaskReadModel {self.id}: {self.description}>'