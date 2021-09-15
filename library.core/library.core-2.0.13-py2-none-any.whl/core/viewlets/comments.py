# -*- coding: utf-8 -*-

from AccessControl import getSecurityManager
from AccessControl import Unauthorized
from Acquisition import aq_inner
from library.core.widget.hidden_honeypot import HiddenHoneyPotFieldWidget
from plone.app.discussion import _
from plone.app.discussion.browser.comments import CommentForm
from plone.app.discussion.browser.comments import CommentsViewlet as baseCommentsViewlet
from plone.app.discussion.browser.validator import CaptchaValidator
from plone.app.discussion.interfaces import ICaptcha
from plone.app.discussion.interfaces import IComment
from plone.app.discussion.interfaces import IConversation
from plone.app.discussion.interfaces import IDiscussionSettings
from plone.app.discussion.interfaces import IReplies
from plone.autoform import directives
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage
from z3c.form import button
from z3c.form import field
from zope.component import queryUtility
from zope import schema


class ICommentWithHoneyPot(IComment):

    honeypot = schema.TextLine(title=(u"Signature"), required=False)


class CommentFormWithHoneyPot(CommentForm):

    fields = field.Fields(ICommentWithHoneyPot).omit(
        "portal_type",
        "__parent__",
        "__name__",
        "comment_id",
        "mime_type",
        "creator",
        "creation_date",
        "modification_date",
        "author_username",
        "title",
    )

    def updateFields(self):
        super(CommentFormWithHoneyPot, self).updateFields()
        self.fields["honeypot"].widgetFactory = HiddenHoneyPotFieldWidget

    def updateWidgets(self):
        super(CommentFormWithHoneyPot, self).updateWidgets()
        self.widgets["honeypot"].label = u""

    @button.buttonAndHandler(_(u"Cancel"))
    def handleCancel(self, action):
        # This method should never be called, it's only there to show
        # a cancel button that is handled by a jQuery method.
        pass  # pragma: no cover

    @button.buttonAndHandler(
        _(u"add_comment_button", default=u"Comment"), name="comment"
    )
    def handleComment(self, action):
        if self.request.form["form.widgets.honeypot"]:
            return
        context = aq_inner(self.context)

        # Check if conversation is enabled on this content object
        if not self.__parent__.restrictedTraverse(
            "@@conversation_view",
        ).enabled():
            raise Unauthorized(
                "Discussion is not enabled for this content object.",
            )

        # Validation form
        data, errors = self.extractData()
        if errors:
            return

        # Validate Captcha
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IDiscussionSettings, check=False)
        portal_membership = getToolByName(self.context, "portal_membership")
        captcha_enabled = settings.captcha != "disabled"
        anonymous_comments = settings.anonymous_comments
        anon = portal_membership.isAnonymousUser()
        if captcha_enabled and anonymous_comments and anon:
            if "captcha" not in data:
                data["captcha"] = u""
            captcha = CaptchaValidator(
                self.context, self.request, None, ICaptcha["captcha"], None
            )
            captcha.validate(data["captcha"])

        # Create comment
        comment = self.create_comment(data)

        # Add comment to conversation
        conversation = IConversation(self.__parent__)
        if data["in_reply_to"]:
            # Add a reply to an existing comment
            conversation_to_reply_to = conversation.get(data["in_reply_to"])
            replies = IReplies(conversation_to_reply_to)
            comment_id = replies.addComment(comment)
        else:
            # Add a comment to the conversation
            comment_id = conversation.addComment(comment)

        # Redirect after form submit:
        # If a user posts a comment and moderation is enabled, a message is
        # shown to the user that his/her comment awaits moderation. If the user
        # has 'review comments' permission, he/she is redirected directly
        # to the comment.
        can_review = getSecurityManager().checkPermission("Review comments", context)
        workflowTool = getToolByName(context, "portal_workflow")
        comment_review_state = workflowTool.getInfoFor(
            comment,
            "review_state",
            None,
        )
        if comment_review_state == "pending" and not can_review:
            # Show info message when comment moderation is enabled
            IStatusMessage(self.context.REQUEST).addStatusMessage(
                _("Your comment awaits moderator approval."), type="info"
            )
            self.request.response.redirect(self.action)
        else:
            # Redirect to comment (inside a content object page)
            self.request.response.redirect(self.action + "#" + str(comment_id))


class CommentsViewlet(baseCommentsViewlet):
    form = CommentFormWithHoneyPot
