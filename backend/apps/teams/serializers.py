"""
Our first serializer! The following guide is amazing: https://github.com/fussionlab/VueJs-Django
"""
from PIL import Image

from rest_framework import serializers
from .models import Team, TeamMember, Player


class PlayerSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    position_display = serializers.CharField(source='get_position_display', read_only=True)
    class Meta:
        model = Player
        fields = ["id","name", "surname","full_name", "main_shirt_number", "position", "position_display", "created_at"]
        read_only_fields = ["id", "full_name", "created_at"]

    def get_full_name(self, obj): # This is how we calculate variables based on the current object with Serializers!
        return f"{obj.name} {obj.surname}"


class TeamMemberSerializer(serializers.ModelSerializer):
    player = PlayerSerializer(read_only=True)
    class Meta:
        model = TeamMember
        fields = ["id", "team", "player", "shirt_number", "joined_at"] # Change this later.
        read_only_fields = ["id", "joined_at"]


class TeamMemberAddSerializer(serializers.ModelSerializer):
    """
    This class is used for adding a member to a team.
    """
    class Meta:
        model = TeamMember
        fields = ["id", "team", "player", "shirt_number", "joined_at"]
        read_only_fields = ["id", "joined_at"]


class TeamSerializer(serializers.ModelSerializer):
    members = TeamMemberSerializer(many=True, read_only=True)
    logo_url = serializers.SerializerMethodField()
    manager_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Team
        fields = ["id", "team_name", "manager_id", "sport_name", "logo_img", "logo_url" ,"members", "created_at"] # This is safer since we decide what can be viewed by VUE
        read_only_fields = ["id", "created_at", "logo_url", "members", "manager_id"]

    def validate_logo_img(self, image):
        max_size = 2 * 1024 * 1024 # 2 MegaBytes
        max_width = 1200
        max_height = 1200
        allowed_content_types = {
            "image/jpg",
            "image/jpeg",
            "image/png",
            "image/webp",
        }

        allowed_image_formats = {"JPG", "JPEG", "PNG", "WEBP"}

        if image.size > max_size:
            raise serializers.ValidationError(
                "Logo image must be smaller than 2 MB."
            )

        content_type = getattr(image, "content_type", None)

        if content_type not in allowed_content_types:
            raise serializers.ValidationError(
                "Only JPG, JPEG, PNG, and WEBP images are allowed."
            )
        # Based on https://gist.github.com/Tanimodori/66336dc8d2eb945711d2ec85beb6438f
        try:
            img = Image.open(image)
            width, height = img.size
            image_format = img.format
            img.verify()
        except (IOError, SyntaxError):
            raise serializers.ValidationError("Invalid image file.")

        image.seek(0)

        if image_format not in allowed_image_formats:
            raise serializers.ValidationError(
                "Only JPG, JPEG, PNG, and WEBP images are allowed."
            )

        if width > max_width or height > max_height:
            raise serializers.ValidationError(
                f"Logo dimensions must be at most {max_width}x{max_height} pixels."
            )

        return image


    def get_logo_url(self, obj):
        if not obj.logo_img:
            return None

        request = self.context.get('request')

        if request:
            return request.build_absolute_uri(obj.logo_img.url)

        return obj.logo_img.url

class addPlayerToTeamSerializer(serializers.Serializer):
    player_id = serializers.PrimaryKeyRelatedField(queryset=Player.objects.all(), source="player")
    shirt_number = serializers.IntegerField(min_value=1, max_value=99)

    def validate_player(self, value):
        try:
            return Player.objects.get(id=value)
        except Player.DoesNotExist:
            raise serializers.ValidationError("Player does not exist")

    def validate(self, attrs):
        team = self.context["team"]
        player = attrs["player"]
        shirt_number = attrs["shirt_number"]

        if TeamMember.objects.filter(team=team, shirt_number=shirt_number).exists():
            raise serializers.ValidationError("Shirt number is already in use")

        if TeamMember.objects.filter(team=team, player=player).exists():
            raise serializers.ValidationError("Player already exists in team")

        return attrs

    def create(self, validated_data):
        team = self.context["team"]
        player = validated_data["player"]
        shirt_number = validated_data["shirt_number"]

        return TeamMember.objects.create(team=team, shirt_number=shirt_number, player=player)