from bson import ObjectId

from app.db.mongodb import get_collection


async def delete_user_account_data(user_id: str) -> None:
    users = get_collection("users")
    refresh_tokens = get_collection("refresh_tokens")
    posts = get_collection("posts")
    friend_requests = get_collection("friend_requests")
    friendships = get_collection("friendships")
    notifications = get_collection("notifications")

    await refresh_tokens.delete_many({"user_id": user_id})
    await posts.delete_many({"author_id": user_id})
    await posts.update_many({}, {"$pull": {"reactions": {"user_id": user_id}}})
    await friend_requests.delete_many({"$or": [{"sender_id": user_id}, {"receiver_id": user_id}]})
    await friendships.delete_many({"users": user_id})
    await notifications.delete_many(
        {
            "$or": [
                {"user_id": user_id},
                {"data.author_id": user_id},
                {"data.sender_id": user_id},
                {"data.reactor_id": user_id},
                {"data.friend_id": user_id},
            ]
        }
    )
    await users.delete_one({"_id": ObjectId(user_id)})
