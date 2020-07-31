import enum

from flask_restx import field
from .app import (
    api,
    db,
)


class ApprovalChoices(enum.Enum):
    NEW = 'new'
    QUESTIONABLE = 'questionable'
    ACCURATE = 'accurate'
    VERIFIED = 'verified'
    DEACTIVATED = 'deactivated'
    ACTIVATED = 'activated'
    STAFF = 'staff'


class ApprovalChange(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    change_from = db.Column(db.Enum(ApprovalChoices))
    change_to = db.Column(db.Enum(ApprovalChoices))
    change_date = db.Column(db.DateTime)
    reasoning = db.Column(db.String)
    content_type = db.Column(String(50))
    object_id = db.Column(db.Integer)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref=db.backref('approval_changes', lazy=True))

    APIModel = api.model('approval_change', {
        'id': fields.Integer(readonly=True, description="The change's unique identifier"),
        'change_from': fields.String(readonly=True, description="What approval level the change moved from", enum=ApprovalChoices._member_names),
        'change_to': fields.String(readonly=False, description="What approval level the change moved to", enum=ApprovalChoices._member_names),
        'change_date': fields.DateTime(readonly=True, description="When the change was made"),
        'reasoning': fields.String(readonly=False, description="The reason for the change"),
        'content_type': fields.String(readonly=False, description="The type of object that was changed"),
        'object_id': fields.Integer(readonly=False, description="The ID of the object that was changed"),
        'user_id': fields.Integer(readonly=True, description="The ID of the user who made the change"),
        'user_display_name': fields.String(readonly=True, description="The name of the user who made the change"),
    )


class ApprovableModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    approval_status = db.Column(db.Enum(ApprovalChoices))
    _approval_changes = None

    @property
    def approval_changes(self):
        if self._approval_changes is None:
            self._approval_changes = ApprovalChange.query.filter_by(object_id=self.id, content_type=self.__tablename__)
        return self._approval_changes


class User(ApprovableModel):
    email = db.Column(db.String(500))
    password = db.Column(db.String(1000))
    display_name = db.Column(db.String(500))
    pronouns = db.Column(db.String(100))  # pronoun.is link
    bio = db.Column(db.String)

    APIModel = api.model('user', {
        'id': fields.Integer(readonly=True, description="The user's unique identifier"),
        'approval_status': 
        'email': fields.String(readonly=False, description="The user's email"),
        'display_name': fields.String(readonly=False, description="The name to display for the user"),
        'password': fields.String(readonly=False, description="The user's password (not in responses)"),
        'pronouns': fields.String(readonly=False, description="The user's pronouns in pronoun.is format"),
        'bio': fields.String(readonly=False, description="A short bio for the user"),
    })
    APIFulFields = ('id', 'email', 'display_name', 'password', 'pronouns', 'bio')
    APIPublicFields = ('id', 'display_name', 'pronouns', 'bio')
    APIShortFields = ('id', 'display_name', 'pronouns')


class Author(ApprovableModel):
    name = db.Column(db.String(500))
    slug = db.Column(db.String(500))
    bio = db.Column(db.String)
    webpage = db.Column(db.String(4500))

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref=db.backref('approval_changes', lazy=True))


genre_exemplars = db.Table('genre_exemplars',
    db.Column('genre_id', db.Integer, db.ForeignKey('genre.id'), primary_key=True),
    db.Column('book_id', db.Integer, db.ForeignKey('book.id'), primary_key=True),
)

class Genre(ApprovableModel):
    name = db.Column(db.String(50))
    slug = db.Column(db.String(50))
    description = db.Column(db.String)
    exemplars = db.relationship('Book', secondary=genre_exemplars, lazy='subquery', backref=db.backref('exemplar_of', lazy=True))

    parent_id = db.Column(db.Integer, db.ForeignKey('genre.id'))
    parent = db.relationship('Genre', backref=db.backref('children', lazy=True))


class Book(ApprovableModel):
    isbn = db.Column(db.String(13), unique=True, blank=True)
    title = db.Column(db.String(5000))
    slug = models.SlugField()
    author = models.ForeignKey('Author', on_delete=models.CASCADE)
    blurb = models.TextField()
    reviews = models.TextField()


class LinkSource(ApprovableModel):
    class TypeChoices(db.Enum):
        ('d', 'Direct-from-creator store'),
        ('i', 'Indie store'),
        ('s', 'Store'),
        ('h', 'Homepage'),
        ('r', 'Review'),
        ('p', 'Publisher'),
        ('o', 'Other'),
    name = db.Column(db.String(max_length=100)
    slug = models.SlugField()
    homepage = models.URLField(blank=True)
    link_type = db.Column(db.String(max_length=1, choices=TYPE_CHOICES)


class Link(ApprovableModel):
    # type: ebook, download, paperback, other
    text = db.Column(db.String)
    book = models.ForeignKey('Book', on_delete=models.CASCADE)
    source = models.ForeignKey('LinkSource', on_delete=models.CASCADE)
    url = models.URLField()
    clicks = models.IntegerField(default=0)
